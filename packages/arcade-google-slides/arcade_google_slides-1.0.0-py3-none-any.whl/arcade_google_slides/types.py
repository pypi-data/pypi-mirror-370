from typing import TypedDict

from arcade_google_slides.enum import PlaceholderType, PredefinedLayout, ShapeType


class Bullet(TypedDict):
    """Partial implementation of the REST Resource Bullet.

    Represents a bullet in a TextElement.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text#Page.Bullet
    """

    nestingLevel: int  # The nesting level of this paragraph in the list.


class ParagraphMarker(TypedDict):
    """Partial implementation of the REST Resource ParagraphMarker.

    Represents a paragraph marker in a TextElement.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text#Page.ParagraphMarker
    """

    bullet: Bullet


class Link(TypedDict):
    """Partial implementation of the REST Resource Link.

    Represents a hypertext link.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/other#Page.Link
    """

    url: str


class TextStyle(TypedDict):
    """Partial implementation of the REST Resource TextStyle.

    Represents the styling that can be applied to a TextRun.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text#Page.TextStyle
    """

    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    link: Link


class TextRun(TypedDict):
    """Partial implementation of the REST Resource TextRun.

    A TextElement kind that represents a run of text that all has the same styling.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text#Page.TextRun
    """

    content: str  # The text of this run.
    style: TextStyle


class TextElementWithParagraphMarker(TypedDict):
    """Partial implementation of the REST Resource TextElement.

    TextElement containing a paragraph marker.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text#Page.TextElement
    """

    paragraphMarker: ParagraphMarker


class TextElementWithTextRun(TypedDict):
    """Partial implementation of the REST Resource TextElement.

    TextElement containing a text run.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text#Page.TextElement
    """

    textRun: TextRun


# https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text#Page.TextElement
TextElement = TextElementWithParagraphMarker | TextElementWithTextRun


class TextContent(TypedDict):
    """Partial implementation of the REST Resource TextContent.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text#Page.TextContent
    """

    textElements: list[TextElement]


class Shape(TypedDict):
    """Partial implementation of the REST Resource Shape.


    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/shapes#Page.Shape
    """

    shapeType: ShapeType
    text: TextContent


class PageElement(TypedDict):
    """Partial implementation of the REST Resource PageElement.

    A visual element on a page.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages#Page.PageElement
    """

    objectId: str
    shape: Shape


class SlideProperties(TypedDict):
    """Partial implementation of the REST Resource SlideProperties.

    The properties of Page that are only relevant for pages with pageType SLIDE.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages#Page.SlideProperties
    """

    # Whether the slide is skipped (hidden) in the presentation mode. Defaults to false.
    isSkipped: bool


class Page(TypedDict):
    """Partial implementation of the REST Resource Page.

    A page is a single slide in a presentation.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages#Page
    """

    objectId: str
    pageElements: list[PageElement]
    slideProperties: SlideProperties


class Presentation(TypedDict):
    """Partial implementation of the REST Resource Presentation.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations#Presentation
    """

    presentationId: str | None  # None when creating a new presentation
    title: str
    slides: list[Page]


class InsertTextRequest(TypedDict):
    """Partial implementation of the REST Resource InsertTextRequest.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#InsertTextRequest
    """

    objectId: str
    text: str


class Placeholder(TypedDict):
    """Partial implementation of the REST Resource Placeholder.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/other#Page.Placeholder
    """

    type: PlaceholderType
    index: int


class LayoutPlaceholderIdMapping(TypedDict):
    """Partial implementation of the REST Resource LayoutPlaceholderIdMapping.

    The user-specified ID mapping for a placeholder that will be
    created on a slide from a specified layout.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#LayoutPlaceholderIdMapping
    """

    objectId: str
    layoutPlaceholder: Placeholder


class LayoutReference(TypedDict):
    """Partial implementation of the REST Resource LayoutReference.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#LayoutReference
    """

    predefinedLayout: PredefinedLayout


class CreateSlideRequest(TypedDict, total=False):
    """Partial implementation of the REST Resource CreateSlideRequest.

    insertionIndex is not required

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#CreateSlideRequest
    """

    objectId: str
    insertionIndex: int  # The zero-based index where the new slide should be inserted. If not provided, the slide will be added to the end of the presentation.  # noqa: E501
    slideLayoutReference: LayoutReference
    placeholderIdMappings: list[LayoutPlaceholderIdMapping]


class Request(TypedDict, total=False):
    """Partial implementation of the REST Resource Request.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#Request
    """

    createSlide: CreateSlideRequest
    insertText: InsertTextRequest
