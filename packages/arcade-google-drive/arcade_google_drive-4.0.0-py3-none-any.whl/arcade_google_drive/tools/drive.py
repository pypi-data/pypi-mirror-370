import base64
import json
from typing import Annotated, Any

from arcade_tdk import ToolContext, ToolMetadataKey, tool
from arcade_tdk.auth import Google
from arcade_tdk.errors import ToolExecutionError
from googleapiclient.errors import HttpError

from arcade_google_drive.enums import Corpora, OrderBy
from arcade_google_drive.types import (
    GoogleDriveFileType,
    SearchMetadata,
)
from arcade_google_drive.utils import (
    SearchQueryBuilder,
    build_drive_service,
    build_file_tree,
    build_file_tree_request_params,
)


@tool(
    requires_auth=Google(
        scopes=["https://www.googleapis.com/auth/drive.file"],
    ),
)
async def get_file_tree_structure(
    context: ToolContext,
    include_shared_drives: Annotated[
        bool, "Whether to include shared drives in the file tree structure. Defaults to False."
    ] = False,
    restrict_to_shared_drive_id: Annotated[
        str | None,
        "If provided, only include files from this shared drive in the file tree structure. "
        "Defaults to None, which will include files and folders from all drives.",
    ] = None,
    include_organization_domain_documents: Annotated[
        bool,
        "Whether to include documents from the organization's domain. This is applicable to admin "
        "users who have permissions to view organization-wide documents in a Google Workspace "
        "account. Defaults to False.",
    ] = False,
    order_by: Annotated[
        list[OrderBy] | None,
        "Sort order. Defaults to listing the most recently modified documents first",
    ] = None,
    limit: Annotated[
        int | None,
        "The number of files and folders to list. Defaults to None, "
        "which will list all files and folders.",
    ] = None,
) -> Annotated[
    dict,
    "A dictionary containing the file/folder tree structure in the user's Google Drive",
]:
    """
    Get the file/folder tree structure of the user's Google Drive.
    """
    service = build_drive_service(context.get_auth_token_or_empty())

    keep_paginating = True
    page_token = None
    files = {}
    file_tree: dict[str, list[dict]] = {"My Drive": []}

    params = build_file_tree_request_params(
        order_by,
        page_token,
        limit,
        include_shared_drives,
        restrict_to_shared_drive_id,
        include_organization_domain_documents,
    )

    while keep_paginating:
        # Get a list of files
        results = service.files().list(**params).execute()

        # Update page token
        page_token = results.get("nextPageToken")
        params["pageToken"] = page_token
        keep_paginating = page_token is not None

        for file in results.get("files", []):
            files[file["id"]] = file

    if not files:
        return {"drives": []}

    file_tree = build_file_tree(files)

    drives = []

    for drive_id, files in file_tree.items():  # type: ignore[assignment]
        if drive_id == "My Drive":
            drive = {"name": "My Drive", "children": files}
        else:
            try:
                drive_details = service.drives().get(driveId=drive_id).execute()
                drive_name = drive_details.get("name", "Shared Drive (name unavailable)")
            except HttpError as e:
                drive_name = (
                    f"Shared Drive (name unavailable: 'HttpError {e.status_code}: {e.reason}')"
                )

            drive = {"name": drive_name, "id": drive_id, "children": files}

        drives.append(drive)

    return {
        "drives": drives,
    }


@tool(
    requires_auth=Google(),
    requires_metadata=[ToolMetadataKey.CLIENT_ID, ToolMetadataKey.COORDINATOR_URL],
)
def generate_google_file_picker_url(
    context: ToolContext,
) -> Annotated[dict, "Google File Picker URL for user file selection and permission granting"]:
    """Generate a Google File Picker URL for user-driven file selection and authorization.

    This tool generates a URL that directs the end-user to a Google File Picker interface where
    where they can select or upload Google Drive files. Users can grant permission to access their
    Drive files, providing a secure and authorized way to interact with their files.

    This is particularly useful when prior tools (e.g., those accessing or modifying
    Google Docs, Google Sheets, etc.) encountered failures due to file non-existence
    (Requested entity was not found) or permission errors. Once the user completes the file
    picker flow, the prior tool can be retried.

    Suggest this tool to users when they are surprised or confused that the file they are
    searching for or attempting to access cannot be found.
    """
    client_id = context.get_metadata(ToolMetadataKey.CLIENT_ID)
    client_id_parts = client_id.split("-")
    if not client_id_parts:
        raise ToolExecutionError(
            message="Invalid Google Client ID",
            developer_message=f"Google Client ID '{client_id}' is not valid",
        )
    app_id = client_id_parts[0]
    cloud_coordinator_url = context.get_metadata(ToolMetadataKey.COORDINATOR_URL).strip("/")

    config = {
        "auth": {
            "client_id": client_id,
            "app_id": app_id,
        },
    }
    config_json = json.dumps(config)
    config_base64 = base64.urlsafe_b64encode(config_json.encode("utf-8")).decode("utf-8")
    url = f"{cloud_coordinator_url}/google/drive_picker?config={config_base64}"

    return {
        "url": url,
        "llm_instructions": (
            "Instruct the user to click the following link to open the Google Drive File Picker. "
            "This will allow them to select files and grant access permissions: {url}"
        ),
    }


@tool(
    requires_auth=Google(
        scopes=["https://www.googleapis.com/auth/drive.file"],
    ),
)
async def search_files(
    context: ToolContext,
    query: Annotated[
        str,
        "The search query to use to find files in Google Drive"
        "This can include document titles or body content.",
    ],
    include_shared_drives: Annotated[
        bool, "Whether to include shared drives in the search. Defaults to False."
    ] = False,
    restrict_to_shared_drive_id: Annotated[
        str | None,
        "If provided, only search files from this shared drive. "
        "Defaults to None, which will search files from all drives.",
    ] = None,
    include_organization_domain_documents: Annotated[
        bool,
        "Whether to include documents from the organization's domain. "
        "This is applicable to admin users who have permissions to view "
        "organization-wide documents in a Google Workspace account. "
        "Defaults to False.",
    ] = False,
    order_by: Annotated[
        list[OrderBy] | None,
        "Sort order for search results. "
        "Defaults to listing the most recently modified documents first. "
        "If the query contains 'fullText', then the order_by will be ignored.",
    ] = None,
    limit: Annotated[
        int | None,
        "The maximum number of search results to return. Defaults to 50.",
    ] = 50,
    file_types: Annotated[
        list[GoogleDriveFileType] | None,
        "Filter by specific file types. Defaults to None, which includes all file types.",
    ] = None,
) -> Annotated[
    dict[str, Any],  # TODO: Change to SearchResult once we have TypedDict support
    "Search results containing matching files from Google Drive with metadata and file information",
]:
    """
    Search for files in Google Drive
    """
    service = build_drive_service(context.get_auth_token_or_empty())

    # Build search query
    search_query = SearchQueryBuilder.build_search_query(query, file_types)

    # Build request parameters
    fields = (
        "files(id, name, mimeType, size, createdTime, modifiedTime, "
        "owners, parents, driveId, webViewLink, thumbnailLink)"
    )
    params = {
        "q": search_query,
        "pageSize": limit,
        "fields": fields,
    }

    # Add ordering
    if "fullText" in search_query:
        # Google drive API does not support other order_by values for
        # queries with fullText search.
        order_by = None
    elif order_by:
        params["orderBy"] = ",".join([item.value for item in order_by])
    else:
        params["orderBy"] = OrderBy.MODIFIED_TIME_DESC.value

    # Add drive-specific parameters
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

    # Execute search
    try:
        results = service.files().list(**params).execute()
        files = results.get("files", [])

        order_by_str = params.get("orderBy")
        if not isinstance(order_by_str, str):
            order_by_str = None

        search_metadata: SearchMetadata = {
            "file_types_filtered": file_types,
            "include_shared_drives": include_shared_drives,
            "order_by": order_by_str,
        }

        response: dict[str, Any] = {
            "query": query,
            "search_query": search_query,
            "total_results": len(files),
            "files": files,
            "search_metadata": search_metadata,
        }

        return response  # noqa: TRY300

    except HttpError as e:
        raise ToolExecutionError(
            message=f"Failed to search Google Drive files: {e.reason}",
            developer_message=f"Google Drive API error: {e.status_code}: {e.reason}",
        )
