import logging
from enum import Enum
from typing import Optional, Type, Any, List, Union, Dict

import fitz
import pymupdf4llm
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field
from pymupdf import Document, Page

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.file_analysis.tool_vars import PDF_TOOL
from codemie_tools.utils.image_processor import ImageProcessor

# Configure logger
logger = logging.getLogger(__name__)

# Constants for error messages
ERROR_NO_PDF_LOADED = "No PDF document is loaded"
ERROR_NO_PDF_LOADED_DETAIL = "No PDF document is loaded. Please provide a valid PDF."

class PdfProcessor:
    """
    A utility class for processing PDFs and extracting text using OCR capabilities.
    Uses ImageProcessor for image-based text extraction and PyMuPDF for PDF processing.
    """

    def __init__(self, chat_model: Optional[BaseChatModel] = None):
        """
        Initialize the OCR processor.

        Args:
            chat_model: Optional LangChain chat model for image text extraction
        """
        self.image_processor = ImageProcessor(chat_model=chat_model) if chat_model else None

    def process_pdf(self, pdf_document: Document, pages: List[int] = None) -> str:
        """
        Process a PDF document and extract text from both regular content and images.

        Args:
            pdf_document: PDF file
            pages: List of 1-based page numbers to process. If None, processes all pages.

        Returns:
            str: Combined extracted text from PDF content and images
        """
        if not pdf_document or getattr(pdf_document, 'is_closed', True):
            logger.error(ERROR_NO_PDF_LOADED)
            raise ValueError(ERROR_NO_PDF_LOADED_DETAIL)

        logger.info("Processing PDF with LLM for image text recognition")

        try:
            return self._process_pdf_document(pdf_document, pages)
        finally:
            pdf_document.close()

    @staticmethod
    def extract_text_as_markdown(pdf_document: Document, pages: List[int] = None,
                                 page_chunks: bool = False) -> str:
        """
        Extract text from a PDF document and format it as markdown.

        Args:
            pdf_document: PyMuPDF document object
            pages: List of 1-based page numbers to process. If None, processes all pages.
            page_chunks: Whether to include page metadata in the output.

        Returns:
            str: Markdown-formatted extracted text from the PDF
        """
        if not pdf_document:
            logger.error(ERROR_NO_PDF_LOADED)
            raise ValueError(ERROR_NO_PDF_LOADED_DETAIL)

        if getattr(pdf_document, 'is_closed', False):
            logger.error("Document is closed")
            raise ValueError("document closed")

        logger.info(f"Extracting text from pages: {pages if pages else 'all'}")

        # Convert 1-based page indices to 0-based for PyMuPDF.
        zero_based_pages = [p - 1 for p in pages] if pages else None

        markdown = pymupdf4llm.to_markdown(
            doc=pdf_document,
            pages=zero_based_pages,
            page_chunks=page_chunks
        )
        logger.debug(f"Extracted {len(markdown)} characters of text")
        return markdown

    @staticmethod
    def get_total_pages(pdf_document: Document) -> str:
        """
        Get the total number of pages in a PDF document.

        Args:
            pdf_document: PyMuPDF document object

        Returns:
            str: Total number of pages as a string
        """
        if not pdf_document or getattr(pdf_document, 'is_closed', True):
            logger.error(ERROR_NO_PDF_LOADED)
            raise ValueError(ERROR_NO_PDF_LOADED_DETAIL)

        logger.debug(f"Returning total page count: {pdf_document.page_count}")
        return str(pdf_document.page_count)

    def _process_pdf_document(self, pdf_document: Document, pages: List[int] = None) -> str:
        """
        Internal method to process a PDF document and extract text.

        Args:
            pdf_document: PyMuPDF document object
            pages: List of 1-based page numbers to process. If None, processes all pages.

        Returns:
            str: Combined extracted text from PDF content and images
        """
        # Convert 1-based page indices to 0-based for PyMuPDF
        zero_based_pages = [p - 1 for p in pages] if pages else list(range(pdf_document.page_count))

        all_text = []

        for page_num in zero_based_pages:
            logger.info(f"Processing page {page_num + 1}")
            page = pdf_document[page_num]

            # Extract text directly from PDF
            text = page.get_text() if hasattr(page, 'get_text') else page.getText()
            if text.strip():
                all_text.append(f"--- Page {page_num + 1} PDF Text ---\n{text}")

            # Process images if image processor is available
            if not self.image_processor:
                continue

            # Extract and process images
            image_text = self._process_page_images(pdf_document, page, page_num)
            if image_text:
                all_text.append(image_text)

        # Combine all extracted text
        result = "\n\n".join(all_text)
        logger.info(f"Processing complete, extracted {len(result)} characters in total")
        return result

    def _process_page_images(self, pdf_document: Document, page: Page, page_num: int) -> Optional[str]:
        """
        Process all images on a single PDF page.

        Args:
            pdf_document: PyMuPDF document object
            page: PyMuPDF page object
            page_num: Zero-based page number

        Returns:
            Optional[str]: Extracted text from images, if any
        """
        image_list = page.get_images(full=True)
        if not image_list:
            logger.debug(f"No images found on page {page_num + 1}")
            return None

        logger.info(f"Found {len(image_list)} images on page {page_num + 1}")
        page_image_texts = []

        for img_idx, img_info in enumerate(image_list):
            try:
                xref = img_info[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                # Use the image processor to extract text
                image_text = self.image_processor.extract_text_from_image_bytes(image_bytes)

                if image_text.strip():
                    page_image_texts.append(
                        f"--- Page {page_num + 1} Image {img_idx + 1} Text ---\n{image_text}"
                    )
                    logger.debug(f"Extracted {len(image_text)} characters from image {img_idx}")
                else:
                    logger.debug(f"No text found in image {img_idx} on page {page_num + 1}")

            except Exception as e:
                logger.error(f"Error processing image {img_idx} on page {page_num + 1}: {str(e)}")

        return "\n\n".join(page_image_texts) if page_image_texts else None

class QueryType(str, Enum):
    TEXT = "Text"
    TEXT_WITH_METADATA = "Text_with_Metadata"
    TEXT_WITH_OCR = "Text_with_Image"  # Kept the name for backward compatibility, now uses LLM
    TOTAL_PAGES = "Total_Pages"


class PDFToolInput(BaseModel):
    """
    Defines the schema for the arguments required by PDFTool.
    """
    pages: list[int] = Field(
        default_factory=list,
        description=(
            "List of page numbers of a PDF document to process. "
            "Must be empty to process all pages in a single request. "
            "Page numbers are 1-based."
        ),
    )
    query: QueryType = Field(
        ...,
        description=(
            "'Text' if the tool must return the text representation of the PDF pages. "
            "'Text_with_Metadata' if the tool must return the text representation of the "
            "PDF pages with metadata. "
            "'Text_with_Image' if the tool must extract text from PDF that contain images within it"
            "'Total_Pages' if the tool must return the total number of pages in the PDF "
            "document."
        ),
    )


class PDFTool(CodeMieTool):
    """
    A tool for processing PDF documents, such as extracting the text from specific pages.
    Also supports text extraction from images within PDFs using LLM-based image recognition.
    """

    # The Pydantic model that describes the shape of arguments this tool takes.
    args_schema: Type[BaseModel] = PDFToolInput

    name: str = PDF_TOOL.name
    label: str = PDF_TOOL.label
    description: str = PDF_TOOL.description

    # High value to support large PDF files.
    tokens_size_limit: int = 100_000

    pdf_document: Optional[Document] = None
    pdf_processor: Optional[PdfProcessor] = None

    # Chat model used for image text extraction
    chat_model: Optional[BaseChatModel] = Field(default=None, exclude=True)

    def __init__(self, file_content: bytes, **kwargs: Any) -> None:
        """
        Initialize the PDFTool with a PDF as bytes.

        Args:
            file_content (bytes): The raw bytes of the PDF file.
            **kwargs: Additional keyword arguments to pass along to the super class.
                      Expects chat_model for image text extraction.
        """
        super().__init__(**kwargs)
        self.pdf_document = fitz.open(stream=file_content, filetype="pdf")
        self.pdf_processor = PdfProcessor(chat_model=self.chat_model)

    def execute(self, pages: List[int], query: QueryType) -> Union[str, Dict[str, Any]]:
        """
        Process the PDF document based on the provided query and pages.

        Args:
            pages (List[int]): A list of 1-based page numbers to process.
                               If empty, the entire document is processed.
            query (str): The query or action to perform:
                - "Total_Pages" to return the total number of pages.
                - "Text" to return the text representation of the PDF.
                - "Text_with_Metadata" to return the text along with metadata.
                - "Text_with_OCR" to extract text from PDF and images using LLM.

        Returns:
            str | dict: A string representation of the requested data or a dictionary with structured results.
        """
        logger.info(f"Processing PDF with query type: {query}")

        if query == QueryType.TOTAL_PAGES:
            return self.pdf_processor.get_total_pages(self.pdf_document)

        elif query == QueryType.TEXT_WITH_OCR:
            return self.pdf_processor.process_pdf(self.pdf_document, pages)

        elif query.lower().startswith("text"):
            # Pass page_chunks parameter based on query type
            page_chunks = (query == QueryType.TEXT_WITH_METADATA)
            return self.pdf_processor.extract_text_as_markdown(
                pdf_document=self.pdf_document,
                pages=pages,
                page_chunks=page_chunks
            )

        else:
            error_msg = (f"Unknown query '{query}'. Expected one of ['Total_Pages', 'Text', "
                        f"'Text_with_Metadata', 'Text_with_OCR'].")
            logger.error(error_msg)
            raise ValueError(error_msg)