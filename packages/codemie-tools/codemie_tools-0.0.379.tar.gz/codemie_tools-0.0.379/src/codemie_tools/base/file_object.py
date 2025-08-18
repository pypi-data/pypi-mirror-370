from typing import Any, Optional

from pydantic import BaseModel

class MimeType:
    """A class to represent the MIME type of a file"""

    IMG_PREFIX = 'image'

    CSV_TYPE = 'text/csv'
    PNG_TYPE = 'image/png'
    PDF_TYPE = 'application/pdf'
    PPTX_TYPE = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

    def __init__(self, mime_type: str):
        self.mime_type = mime_type

    @property
    def is_image(self) -> bool:
        """Check if the mime type is an image"""
        return self.mime_type.startswith(self.IMG_PREFIX)

    @property
    def is_csv(self) -> bool:
        """Check if the mime type is a CSV file"""
        return self.mime_type == self.CSV_TYPE

    @property
    def is_png(self) -> bool:
        """Check if the mime type is a PNG image"""
        return self.mime_type == self.PNG_TYPE

    @property
    def is_pdf(self) -> bool:
        """Check if the mime type is a PDF file"""
        return self.mime_type == self.PDF_TYPE

    @property
    def is_pptx(self) -> bool:
        """Check if the mime type is a PPTX (PowerPoint) file"""
        return self.mime_type == self.PPTX_TYPE

    @property
    def is_text_based(self) -> bool:
        """Check if the mime type is text-based"""
        return self.mime_type is not None and self.mime_type.startswith('text')

class FileObject(BaseModel):

    """
    A representation of a file object.

    Attributes:
        name (str): The name of the file.
        mime_type (str): The type of the file.
        path (str): The path where the file is located.
        owner (str): The owner of the file.
        content (Any, optional): The content of the file. Defaults to None.
    """
    name: str
    mime_type: str
    path: str
    owner: str
    content: Optional[Any] = None