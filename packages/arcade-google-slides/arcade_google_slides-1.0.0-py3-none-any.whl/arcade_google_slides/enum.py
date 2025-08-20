from enum import Enum


class PredefinedLayout(str, Enum):
    """Partial implementation of the REST Resource PredefinedLayout.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#PredefinedLayout
    """

    BLANK = "BLANK"  # Blank layout, with no placeholders.
    CAPTION_ONLY = "CAPTION_ONLY"  # Layout with a caption at the bottom.
    TITLE = "TITLE"  # Layout with a title and a subtitle.
    TITLE_AND_BODY = "TITLE_AND_BODY"  # Layout with a title and body.
    TITLE_AND_TWO_COLUMNS = "TITLE_AND_TWO_COLUMNS"  # Layout with a title and two columns.
    TITLE_ONLY = "TITLE_ONLY"  # Layout with only a title.
    SECTION_HEADER = "SECTION_HEADER"  # Layout with a section title.
    SECTION_TITLE_AND_DESCRIPTION = "SECTION_TITLE_AND_DESCRIPTION"  # Layout with a title and subtitle on one side and description on the other.  # noqa: E501
    ONE_COLUMN_TEXT = (
        "ONE_COLUMN_TEXT"  # Layout with one title and one body, arranged in a single column.
    )
    MAIN_POINT = "MAIN_POINT"  # Layout with a main point.
    BIG_NUMBER = "BIG_NUMBER"  # Layout with a big number heading.


class ShapeType(Enum):
    """
    The type of shape. For now, only TEXT_BOX is supported.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/shapes#type
    """

    TEXT_BOX = "TEXT_BOX"
    # TODO: Support rectangle or table cell?


class PlaceholderType(str, Enum):
    """Partial implementation of the REST Resource 'Type'.

    The type of placeholder shape.

    Reference: https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/other#Page.Type_3
    """

    TITLE = "TITLE"
    BODY = "BODY"


# --------------------------------------------------------- #
# Drive API Enums
# --------------------------------------------------------- #


class Corpora(str, Enum):
    """
    Bodies of items (files/documents) to which the query applies.
    Prefer 'user' or 'drive' to 'allDrives' for efficiency.
    By default, corpora is set to 'user'.
    """

    USER = "user"
    DOMAIN = "domain"
    DRIVE = "drive"
    ALL_DRIVES = "allDrives"


class DocumentFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    GOOGLE_API_JSON = "google_api_json"


class OrderBy(str, Enum):
    """
    Sort keys for ordering files in Google Drive.
    Each key has both ascending and descending options.
    """

    CREATED_TIME = (
        # When the file was created (ascending)
        "createdTime"
    )
    CREATED_TIME_DESC = (
        # When the file was created (descending)
        "createdTime desc"
    )
    FOLDER = (
        # The folder ID, sorted using alphabetical ordering (ascending)
        "folder"
    )
    FOLDER_DESC = (
        # The folder ID, sorted using alphabetical ordering (descending)
        "folder desc"
    )
    MODIFIED_BY_ME_TIME = (
        # The last time the file was modified by the user (ascending)
        "modifiedByMeTime"
    )
    MODIFIED_BY_ME_TIME_DESC = (
        # The last time the file was modified by the user (descending)
        "modifiedByMeTime desc"
    )
    MODIFIED_TIME = (
        # The last time the file was modified by anyone (ascending)
        "modifiedTime"
    )
    MODIFIED_TIME_DESC = (
        # The last time the file was modified by anyone (descending)
        "modifiedTime desc"
    )
    NAME = (
        # The name of the file, sorted using alphabetical ordering (e.g., 1, 12, 2, 22) (ascending)
        "name"
    )
    NAME_DESC = (
        # The name of the file, sorted using alphabetical ordering (e.g., 1, 12, 2, 22) (descending)
        "name desc"
    )
    NAME_NATURAL = (
        # The name of the file, sorted using natural sort ordering (e.g., 1, 2, 12, 22) (ascending)
        "name_natural"
    )
    NAME_NATURAL_DESC = (
        # The name of the file, sorted using natural sort ordering (e.g., 1, 2, 12, 22) (descending)
        "name_natural desc"
    )
    QUOTA_BYTES_USED = (
        # The number of storage quota bytes used by the file (ascending)
        "quotaBytesUsed"
    )
    QUOTA_BYTES_USED_DESC = (
        # The number of storage quota bytes used by the file (descending)
        "quotaBytesUsed desc"
    )
    RECENCY = (
        # The most recent timestamp from the file's date-time fields (ascending)
        "recency"
    )
    RECENCY_DESC = (
        # The most recent timestamp from the file's date-time fields (descending)
        "recency desc"
    )
    SHARED_WITH_ME_TIME = (
        # When the file was shared with the user, if applicable (ascending)
        "sharedWithMeTime"
    )
    SHARED_WITH_ME_TIME_DESC = (
        # When the file was shared with the user, if applicable (descending)
        "sharedWithMeTime desc"
    )
    STARRED = (
        # Whether the user has starred the file (ascending)
        "starred"
    )
    STARRED_DESC = (
        # Whether the user has starred the file (descending)
        "starred desc"
    )
    VIEWED_BY_ME_TIME = (
        # The last time the file was viewed by the user (ascending)
        "viewedByMeTime"
    )
    VIEWED_BY_ME_TIME_DESC = (
        # The last time the file was viewed by the user (descending)
        "viewedByMeTime desc"
    )
