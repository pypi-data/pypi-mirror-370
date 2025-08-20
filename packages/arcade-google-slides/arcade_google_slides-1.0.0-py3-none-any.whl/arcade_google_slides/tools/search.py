from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Google

from arcade_google_slides.enum import OrderBy
from arcade_google_slides.utils import (
    build_drive_service,
    build_files_list_params,
)


# Implements: https://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.files.html#list
# Example `arcade chat` query: `list my 5 most recently modified presentations`
# TODO: Support query with natural language. Currently, the tool expects a fully formed query
#       string as input with the syntax defined here: https://developers.google.com/drive/api/guides/search-files
@tool(
    requires_auth=Google(
        scopes=["https://www.googleapis.com/auth/drive.file"],
    ),
)
async def search_presentations(
    context: ToolContext,
    presentation_contains: Annotated[
        list[str] | None,
        "Keywords or phrases that must be in the presentation title or content. Provide a list of "
        "keywords or phrases if needed.",
    ] = None,
    presentation_not_contains: Annotated[
        list[str] | None,
        "Keywords or phrases that must NOT be in the presentation title or content. "
        "Provide a list of keywords or phrases if needed.",
    ] = None,
    search_only_in_shared_drive_id: Annotated[
        str | None,
        "The ID of the shared drive to restrict the search to. If provided, the search will only "
        "return presentations from this drive. Defaults to None, which searches across all drives.",
    ] = None,
    include_shared_drives: Annotated[
        bool,
        "Whether to include presentations from shared drives. Defaults to False (searches only in "
        "the user's 'My Drive').",
    ] = False,
    include_organization_domain_presentations: Annotated[
        bool,
        "Whether to include presentations from the organization's domain. "
        "This is applicable to admin users who have permissions to view "
        "organization-wide presentations in a Google Workspace "
        "account. Defaults to False.",
    ] = False,
    order_by: Annotated[
        list[OrderBy] | None,
        "Sort order. Defaults to listing the most recently modified presentations first. "
        "If presentation_contains or presentation_not_contains is provided, "
        "then the order_by will be ignored.",
    ] = None,
    limit: Annotated[int, "The number of presentations to list"] = 50,
    pagination_token: Annotated[
        str | None, "The pagination token to continue a previous request"
    ] = None,
) -> Annotated[
    dict,
    "A dictionary containing 'presentations_count' (number of presentations returned) "
    "and 'presentations' (a list of presentation details including 'kind', 'mimeType', "
    "'id', and 'name' for each presentation)",
]:
    """
    Searches for presentations in the user's Google Drive.
    Excludes presentations that are in the trash.
    """
    if presentation_contains or presentation_not_contains:
        # Google drive API does not support other order_by values for
        # queries with fullText search (which is used when presentation_contains
        # or presentation_not_contains is provided).
        order_by = None
    elif order_by is None:
        order_by = [OrderBy.MODIFIED_TIME_DESC]
    elif isinstance(order_by, OrderBy):
        order_by = [order_by]

    page_size = min(10, limit)
    files: list[dict[str, Any]] = []

    service = build_drive_service(context.get_auth_token_or_empty())

    params = build_files_list_params(
        mime_type="application/vnd.google-apps.presentation",
        document_contains=presentation_contains,
        document_not_contains=presentation_not_contains,
        page_size=page_size,
        order_by=order_by,
        pagination_token=pagination_token,
        include_shared_drives=include_shared_drives,
        search_only_in_shared_drive_id=search_only_in_shared_drive_id,
        include_organization_domain_documents=include_organization_domain_presentations,
    )

    while len(files) < limit:
        if pagination_token:
            params["pageToken"] = pagination_token
        else:
            params.pop("pageToken", None)

        results = service.files().list(**params).execute()
        batch = results.get("files", [])
        files.extend(batch[: limit - len(files)])

        pagination_token = results.get("nextPageToken")
        if not pagination_token or len(batch) < page_size:
            break

    return {
        "presentations_count": len(files),
        "presentations": files,
        "llm_instructions": (
            "If the results were not satisfactory, then inform the user that "
            "you can also search across all of their shared drives."
        ),
    }
