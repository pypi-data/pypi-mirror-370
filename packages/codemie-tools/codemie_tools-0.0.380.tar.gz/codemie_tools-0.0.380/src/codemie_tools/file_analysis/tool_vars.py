from codemie_tools.base.models import ToolMetadata

FILE_ANALYSIS_TOOL = ToolMetadata(
    name="file_analysis",
    description="Tool for analyzing and extracting data from files of various formats",
    label="File Analysis",
)

PPTX_TOOL = ToolMetadata(
    name="pptx_tool",
    description="A tool for extracting content from PPTX documents.",
    label="PPTX Processing Tool",
)

PDF_TOOL = ToolMetadata(
    name="pdf_tool",
    description="A tool for extracting content from PDF documents, including text extraction from embedded images using LLM-based image recognition.",
    label="PDF Processing Tool",
)

CSV_TOOL = ToolMetadata(
    name="csv_tool",
    description="Tool for working with data from CSV files.",
    label="CSV Interpretation",
)
