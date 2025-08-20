import uuid
from typing import Annotated

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Google

from arcade_google_slides.enum import PlaceholderType
from arcade_google_slides.types import (
    Page,
    PredefinedLayout,
    Presentation,
    Request,
)
from arcade_google_slides.utils import build_slides_service, create_blank_presentation


@tool(
    requires_auth=Google(
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
        ],
    )
)
async def create_presentation(
    context: ToolContext,
    title: Annotated[str, "The title of the presentation to create"],
    subtitle: Annotated[str | None, "The subtitle of the presentation to create"] = None,
) -> Annotated[dict, "The created presentation's title, presentationId, and presentationUrl"]:
    """
    Create a new Google Slides presentation
    The first slide will be populated with the specified title and subtitle.
    """
    service = build_slides_service(context.get_auth_token_or_empty())

    presentation: Presentation = create_blank_presentation(service, title)

    slide: Page = presentation["slides"][0]
    title_text_box_id = slide["pageElements"][0]["objectId"]
    subtitle_text_box_id = slide["pageElements"][1]["objectId"]

    requests: list[Request] = [
        {
            "insertText": {
                "objectId": title_text_box_id,
                "text": title,
            }
        },
        {
            "insertText": {
                "objectId": subtitle_text_box_id,
                "text": subtitle if subtitle else "",
            }
        },
    ]

    service.presentations().batchUpdate(
        presentationId=presentation["presentationId"], body={"requests": requests}
    ).execute()

    return {
        "presentation_title": presentation["title"],
        "presentation_id": presentation["presentationId"],
        "presentation_url": f"https://docs.google.com/presentation/d/{presentation['presentationId']}/edit",
    }


@tool(
    requires_auth=Google(
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
        ],
    )
)
async def create_slide(
    context: ToolContext,
    presentation_id: Annotated[str, "The ID of the presentation to create the slide in"],
    slide_title: Annotated[str, "The title of the slide to create"],
    slide_body: Annotated[str, "The body (text) of the slide to create"],
) -> Annotated[dict, "A URL to the created slide"]:
    """Create a new slide at the end of the specified presentation"""
    service = build_slides_service(context.get_auth_token_or_empty())

    title_id = str(uuid.uuid4())[:8]
    body_id = str(uuid.uuid4())[:8]

    create_slide_request: Request = {
        "createSlide": {
            "objectId": "",  # NOTE: We can utilize creating custom IDs for easier lookup/edits
            "slideLayoutReference": {
                "predefinedLayout": PredefinedLayout.TITLE_AND_BODY,
            },
            "placeholderIdMappings": [
                {
                    "layoutPlaceholder": {"type": PlaceholderType.TITLE, "index": 0},
                    "objectId": title_id,
                },
                {
                    "layoutPlaceholder": {"type": PlaceholderType.BODY, "index": 0},
                    "objectId": body_id,
                },
            ],
        },
    }

    insert_text_requests: list[Request] = [
        {"insertText": {"objectId": title_id, "text": slide_title}},
        {"insertText": {"objectId": body_id, "text": slide_body}},
    ]

    response = (
        service.presentations()
        .batchUpdate(
            presentationId=presentation_id,
            body={"requests": [create_slide_request, *insert_text_requests]},
        )
        .execute()
    )

    slide_id = response["replies"][0]["createSlide"]["objectId"]
    return {
        "slide_url": f"https://docs.google.com/presentation/d/{presentation_id}/edit?slide=id.{slide_id}"
    }
