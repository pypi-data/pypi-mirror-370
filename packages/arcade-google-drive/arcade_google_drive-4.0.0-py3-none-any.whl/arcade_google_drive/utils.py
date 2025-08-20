import logging
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build

from arcade_google_drive.enums import Corpora, OrderBy
from arcade_google_drive.types import (
    GoogleDriveFileType,
    get_google_drive_mime_type,
)

## Set up basic configuration for logging to the console with DEBUG level and a specific format.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def build_drive_service(auth_token: str | None) -> Resource:  # type: ignore[no-any-unimported]
    """
    Build a Drive service object.
    """
    auth_token = auth_token or ""
    return build("drive", "v3", credentials=Credentials(auth_token))


def build_file_tree_request_params(
    order_by: list[OrderBy] | None,
    page_token: str | None,
    limit: int | None,
    include_shared_drives: bool,
    restrict_to_shared_drive_id: str | None,
    include_organization_domain_documents: bool,
) -> dict[str, Any]:
    if order_by is None:
        order_by = [OrderBy.MODIFIED_TIME_DESC]
    elif isinstance(order_by, OrderBy):
        order_by = [order_by]

    params = {
        "q": "trashed = false",
        "corpora": Corpora.USER.value,
        "pageToken": page_token,
        "fields": (
            "files(id, name, parents, mimeType, driveId, size, createdTime, modifiedTime, owners)"
        ),
        "orderBy": ",".join([item.value for item in order_by]),
    }

    if limit:
        params["pageSize"] = str(limit)

    if (
        include_shared_drives
        or restrict_to_shared_drive_id
        or include_organization_domain_documents
    ):
        params["includeItemsFromAllDrives"] = "true"
        params["supportsAllDrives"] = "true"

    if restrict_to_shared_drive_id:
        params["driveId"] = restrict_to_shared_drive_id
        params["corpora"] = Corpora.DRIVE.value

    if include_organization_domain_documents:
        params["corpora"] = Corpora.DOMAIN.value

    return params


def build_file_tree(files: dict[str, Any]) -> dict[str, Any]:
    file_tree: dict[str, Any] = {}

    for file in files.values():
        owners = file.get("owners", [])
        if owners:
            owners = [
                {"name": owner.get("displayName", ""), "email": owner.get("emailAddress", "")}
                for owner in owners
            ]
            file["owners"] = owners

        if "size" in file:
            file["size"] = {"value": int(file["size"]), "unit": "bytes"}

        # Although "parents" is a list, a file can only have one parent
        try:
            parent_id = file["parents"][0]
            del file["parents"]
        except (KeyError, IndexError):
            parent_id = None

        # Determine the file's Drive ID
        if "driveId" in file:
            drive_id = file["driveId"]
            del file["driveId"]
        # If a shared drive id is not present, the file is in "My Drive"
        else:
            drive_id = "My Drive"

        if drive_id not in file_tree:
            file_tree[drive_id] = []

        # Root files will have the Drive's id as the parent. If the parent id is not in the files
        # list, the file must be at drive's root
        if parent_id not in files:
            file_tree[drive_id].append(file)

        # Associate the file with its parent
        else:
            if "children" not in files[parent_id]:
                files[parent_id]["children"] = []
            files[parent_id]["children"].append(file)

    return file_tree


class SearchQueryBuilder:
    """Utility class for building Google Drive search queries."""

    @staticmethod
    def _escape_query(query: str) -> str:
        """Escape special characters in the query string for Google Drive search.  https://developers.google.com/workspace/drive/api/guides/search-files#examples"""
        # Escape backslashes first, then apostrophes
        escaped = query.replace("\\", "\\\\").replace("'", "\\'")
        return escaped

    @staticmethod
    def build_search_query(query: str, file_types: list[GoogleDriveFileType] | None) -> str:
        """Build the Google Drive search query string."""
        search_terms = []

        # Add the main query
        if query.strip():
            escaped_query = SearchQueryBuilder._escape_query(query.strip())
            search_terms.append(f"fullText contains '{escaped_query}'")

        # Add file type filters
        if file_types:
            type_conditions = []
            for file_type in file_types:
                mime_types = get_google_drive_mime_type(file_type)
                for mime_type in mime_types:
                    type_conditions.append(f"mimeType = '{mime_type}'")
            if type_conditions:
                search_terms.append(f"({' or '.join(type_conditions)})")

        # Always exclude trashed files
        search_terms.append("trashed = false")

        # Combine all search terms
        return " and ".join(search_terms) if search_terms else "trashed = false"

    @staticmethod
    def _add_date_range_filter(search_terms: list[str], date_range: str) -> None:
        """Add date range filter to search terms."""
        if "last" in date_range.lower():
            if "7 days" in date_range.lower() or "week" in date_range.lower():
                search_terms.append("modifiedTime > '7 days ago'")
            elif "month" in date_range.lower():
                search_terms.append("modifiedTime > '30 days ago'")
            elif "year" in date_range.lower():
                search_terms.append("modifiedTime > '365 days ago'")
        elif " to " in date_range:
            try:
                start_date, end_date = date_range.split(" to ")
                date_condition = f"modifiedTime >= '{start_date.strip()}' and modifiedTime <= '{end_date.strip()}'"  # noqa: E501
                search_terms.append(date_condition)
            except ValueError:
                pass  # Invalid date format, skip date filtering
