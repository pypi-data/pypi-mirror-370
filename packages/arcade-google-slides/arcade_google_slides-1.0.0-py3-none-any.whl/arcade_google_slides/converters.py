"""
Modular converter class for converting Google Slides presentations to Markdown.
This converter strictly follows the TypedDict structure definitions.
"""

import logging

from arcade_google_slides.types import (
    Bullet,
    Page,
    PageElement,
    ParagraphMarker,
    Presentation,
    Shape,
    TextContent,
    TextElement,
    TextRun,
)

logger = logging.getLogger(__name__)


class BulletConverter:
    """Converts bullet elements to markdown."""

    def convert(self, bullet: Bullet) -> str:
        """
        Convert a bullet to markdown representation.

        Args:
            bullet: Bullet TypedDict with glyph and nestingLevel

        Returns:
            Markdown string with appropriate indentation and markdown bullet syntax
        """
        nesting_level = bullet.get("nestingLevel", 0)
        indent = "  " * nesting_level
        return f"{indent}* "


class ParagraphMarkerConverter:
    """Converts paragraph markers to markdown."""

    def __init__(self) -> None:
        self.bullet_converter = BulletConverter()

    def convert(self, paragraph_marker: ParagraphMarker) -> str:
        """
        Convert a paragraph marker to markdown.

        Args:
            paragraph_marker: ParagraphMarker TypedDict

        Returns:
            Markdown string representation
        """
        if "bullet" in paragraph_marker:
            return self.bullet_converter.convert(paragraph_marker["bullet"])
        return ""


class TextRunConverter:
    """Converts text runs to markdown with styling support."""

    def convert(self, text_run: TextRun) -> str:
        """
        Convert a text run to markdown with styling.

        Args:
            text_run: TextRun TypedDict with content and optional style

        Returns:
            The text content with markdown formatting applied
        """
        content = text_run.get("content", "")

        style = text_run.get("style")
        if not style:
            return content

        # Extract leading and trailing spaces to apply formatting correctly
        # Markdown formatting must be adjacent to text, not spaces
        leading_spaces = len(content) - len(content.lstrip())
        trailing_spaces = len(content) - len(content.rstrip())

        # Get the spaces
        prefix = content[:leading_spaces] if leading_spaces > 0 else ""
        suffix = content[-trailing_spaces:] if trailing_spaces > 0 else ""

        trimmed_content = content.strip()

        if not trimmed_content:
            return content

        # Apply text formatting to the trimmed content
        # Note: Order matters for proper markdown rendering

        if style.get("strikethrough", False):
            trimmed_content = f"~~{trimmed_content}~~"

        is_bold = style.get("bold", False)
        is_italic = style.get("italic", False)

        if is_bold and is_italic:
            # Both bold and italic: ***text***
            trimmed_content = f"***{trimmed_content}***"
        elif is_bold:
            # Bold only: **text**
            trimmed_content = f"**{trimmed_content}**"
        elif is_italic:
            # Italic only: *text*
            trimmed_content = f"*{trimmed_content}*"

        # Note: This may not render in all markdown viewers
        if style.get("underline", False):
            trimmed_content = f"<u>{trimmed_content}</u>"

        link = style.get("link")
        if link:
            url = link.get("url", "")
            if url:
                trimmed_content = f"[{trimmed_content}]({url})"

        return prefix + trimmed_content + suffix


class TextElementConverter:
    """Converts text elements to markdown."""

    def __init__(self) -> None:
        self.paragraph_marker_converter = ParagraphMarkerConverter()
        self.text_run_converter = TextRunConverter()

    def convert(self, text_element: TextElement) -> str:
        """
        Convert a text element to markdown.

        Args:
            text_element: Either TextElementWithParagraphMarker or TextElementWithTextRun

        Returns:
            Markdown string representation
        """
        if "paragraphMarker" in text_element:
            return self.paragraph_marker_converter.convert(text_element["paragraphMarker"])  # type: ignore[typeddict-item]

        elif "textRun" in text_element:
            return self.text_run_converter.convert(text_element["textRun"])

        return ""


class TextContentConverter:
    """Converts text content to markdown."""

    def __init__(self) -> None:
        self.text_element_converter = TextElementConverter()

    def convert(self, text_content: TextContent) -> str:
        """
        Convert text content to markdown.

        Args:
            text_content: TextContent TypedDict with textElements list

        Returns:
            Markdown string representation
        """
        markdown_parts = []

        text_elements = text_content.get("textElements", [])

        current_line = ""
        for element in text_elements:
            converted = self.text_element_converter.convert(element)

            # If it's a bullet marker, start a new line if needed
            if "paragraphMarker" in element and "bullet" in element["paragraphMarker"]:  # type: ignore[typeddict-item]
                if current_line:
                    markdown_parts.append(current_line)
                current_line = converted
            else:
                current_line += converted

                # Check if the text run ends with a newline
                if "textRun" in element:
                    content = element["textRun"].get("content", "")  # type: ignore[typeddict-item]
                    if content.endswith("\n"):
                        markdown_parts.append(current_line.rstrip("\n"))
                        current_line = ""

        # Add any remaining text
        if current_line:
            markdown_parts.append(current_line)

        return "\n".join(markdown_parts)


class ShapeConverter:
    """Converts shapes to markdown."""

    def __init__(self) -> None:
        self.text_content_converter = TextContentConverter()

    def convert(self, shape: Shape) -> str:
        """
        Convert a shape to markdown.

        Args:
            shape: Shape TypedDict with shapeType and text

        Returns:
            Markdown string representation
        """
        markdown = ""

        if "text" in shape:
            text_markdown = self.text_content_converter.convert(shape["text"])
            if text_markdown:
                markdown += text_markdown
                if not text_markdown.endswith("\n"):
                    markdown += "\n"

        return markdown


class PageElementConverter:
    """Converts page elements to markdown."""

    def __init__(self) -> None:
        self.shape_converter = ShapeConverter()

    def convert(self, page_element: PageElement) -> str:
        """
        Convert a page element to markdown.

        Args:
            page_element: PageElement TypedDict with objectId and shape

        Returns:
            Markdown string representation
        """
        if "shape" in page_element:
            return self.shape_converter.convert(page_element["shape"])
        return ""


class PageConverter:
    """Converts pages (slides) to markdown."""

    def __init__(self) -> None:
        self.page_element_converter = PageElementConverter()

    def convert(self, page: Page, page_number: int) -> str:
        """
        Convert a page (slide) to markdown.

        Args:
            page: Page TypedDict with objectId and pageElements
            page_number: The page/slide number (1-indexed)

        Returns:
            Markdown string representation
        """
        is_hidden = page.get("slideProperties", {}).get("isSkipped", False)
        is_hidden_str = " (hidden)" if is_hidden else ""
        markdown = f"## Slide {page_number}{is_hidden_str}\n\n"

        slide_id = page.get("objectId", "")
        if slide_id:
            markdown += f"**Slide ID:** {slide_id}\n\n"

        # Process all page elements
        page_elements = page.get("pageElements", [])
        for element in page_elements:
            element_markdown = self.page_element_converter.convert(element)
            if element_markdown:
                markdown += element_markdown
                if not element_markdown.endswith("\n\n"):
                    markdown += "\n"

        return markdown


class PresentationMarkdownConverter:
    """
    Main converter class for converting Google Slides presentations to markdown.
    This converter strictly follows the TypedDict structure definitions.
    """

    def __init__(self) -> None:
        self.page_converter = PageConverter()

    def convert(self, presentation: Presentation) -> str:
        """
        Convert a Google Slides presentation to markdown format.

        Args:
            presentation: Presentation TypedDict with presentationId, title, and slides

        Returns:
            A markdown string representation of the presentation
        """
        if not presentation:
            return ""

        # Extract metadata
        title = presentation.get("title", "Untitled Presentation")
        presentation_id = presentation.get("presentationId", "")
        slides = presentation.get("slides", [])

        # Build markdown
        markdown = f"# {title}\n\n"

        if presentation_id:
            markdown += f"**Presentation ID:** {presentation_id}\n\n"

        if slides:
            markdown += "---\n\n"

            for i, slide in enumerate(slides, 1):
                slide_markdown = self.page_converter.convert(slide, i)
                markdown += slide_markdown

                # Adds separator between slides
                if i < len(slides):
                    markdown += "\n---\n\n"

        return markdown.strip()
