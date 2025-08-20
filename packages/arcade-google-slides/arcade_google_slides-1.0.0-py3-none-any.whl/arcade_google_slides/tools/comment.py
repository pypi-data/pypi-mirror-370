from typing import Annotated

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Google

from arcade_google_slides.utils import build_drive_service


@tool(
    requires_auth=Google(
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
        ],
    )
)
async def comment_on_presentation(
    context: ToolContext,
    presentation_id: Annotated[str, "The ID of the presentation to comment on"],
    comment_text: Annotated[str, "The comment to add to the slide"],
) -> Annotated[dict, "The comment's ID, presentationId, and slideNumber in a dictionary"]:
    """
    Comment on a specific slide by its index in a Google Slides presentation.
    """
    drive_service = build_drive_service(context.get_auth_token_or_empty())

    # Get the presentation
    response = (
        drive_service.comments()
        .create(
            fileId=presentation_id,
            body={
                "content": comment_text,
            },
            fields="id",
        )
        .execute()
    )

    return {
        "comment_id": response["id"],
        "presentation_url": f"https://docs.google.com/presentation/d/{presentation_id}",
    }


@tool(
    requires_auth=Google(
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
        ],
    )
)
async def list_presentation_comments(
    context: ToolContext,
    presentation_id: Annotated[str, "The ID of the presentation to list comments for"],
    include_deleted: Annotated[
        bool,
        "Whether to include deleted comments in the results. Defaults to False.",
    ] = False,
) -> Annotated[
    dict,
    "A dictionary containing the comments",
]:
    """
    List all comments on the specified Google Slides presentation.
    """
    drive_service = build_drive_service(context.get_auth_token_or_empty())

    comments: list[dict] = []
    params: dict = {
        "fileId": presentation_id,
        "pageSize": 100,
        "fields": (
            "nextPageToken,comments(id,content,createdTime,modifiedTime,deleted,"
            "author(displayName,emailAddress),replies(id,content,createdTime,modifiedTime,deleted,author(displayName,emailAddress)))"
        ),
    }
    if include_deleted:
        params["includeDeleted"] = True

    while True:
        results = drive_service.comments().list(**params).execute()
        batch = results.get("comments", [])
        comments.extend(batch)
        next_page_token = results.get("nextPageToken")
        if not next_page_token:
            break
        params["pageToken"] = next_page_token

    reply_count = 0
    for comment in comments:
        reply_count += len(comment.get("replies", []))

    return {
        "comments_count": len(comments),
        "replies_count": reply_count,
        "total_discussion_count": len(comments) + reply_count,
        "comments": comments,
        "presentation_url": f"https://docs.google.com/presentation/d/{presentation_id}",
    }
