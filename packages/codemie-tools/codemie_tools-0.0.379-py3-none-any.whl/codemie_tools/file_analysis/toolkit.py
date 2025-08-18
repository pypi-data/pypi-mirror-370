import io
import warnings
import pandas as pd

from typing import Dict, Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_experimental.tools import PythonAstREPLTool

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.file_object import MimeType
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.file_analysis.file_analysis_tool import FileAnalysisTool
from codemie_tools.file_analysis.pptx_tool import PPTXTool
from codemie_tools.file_analysis.pdf_tool import PDFTool
from codemie_tools.file_analysis.csv_tool import CSVTool, get_csv_delimiter
from codemie_tools.file_analysis.tool_vars import FILE_ANALYSIS_TOOL, PPTX_TOOL, PDF_TOOL, CSV_TOOL


class FileAnalysisToolkit(BaseToolkit):
    model_config = {
        "arbitrary_types_allowed": True
    }
    file_content: Optional[bytes|str] = None
    file_name: Optional[str] = None
    mime_type: Optional[MimeType] = None
    chat_model: Optional[BaseChatModel] = None
    warnings_length_limit: int = 30

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        return ToolKit(
            toolkit=ToolSet.FILE_ANALYSIS,
            tools=[
                Tool.from_metadata(FILE_ANALYSIS_TOOL),
                Tool.from_metadata(PPTX_TOOL),
                Tool.from_metadata(PDF_TOOL),
                Tool.from_metadata(CSV_TOOL),
            ]
        ).model_dump()

    def get_tools(self):
        tools = []
        if not self.file_content:
            return tools
        if self.mime_type.is_pptx:
            tools.append(PPTXTool(file_content=self.file_content, chat_model=self.chat_model))
        elif self.mime_type.is_pdf:
            tools.append(PDFTool(file_content=self.file_content, chat_model=self.chat_model))
        elif self.mime_type.is_csv:
            with warnings.catch_warnings(record=True) as wlist:
                data_frame = pd.read_csv(
                    io.StringIO(self.file_content),
                    delimiter=get_csv_delimiter(self.file_content, 128),
                    on_bad_lines="warn"
                )
            read_csv_warnings = [str(warning.message) for warning in wlist[:self.warnings_length_limit]]
            warnings_string = "\n".join(read_csv_warnings) if read_csv_warnings else None

            df_locals = {"df": data_frame}
            repl_tool = PythonAstREPLTool(locals=df_locals)
            repl_tool.description = self._generate_csv_prompt(self.file_name,
                                                              warnings_string)

            csv_tool = CSVTool(file_content=self.file_content)
            tools.extend([repl_tool, csv_tool])
        else:
            tools.append(FileAnalysisTool(file_content=self.file_content))
        return tools

    @classmethod
    def get_toolkit(cls, mime_type: str, configs: Dict[str, Any], chat_model: Optional[BaseChatModel] = None):
        file_content = configs.get("file_content", None)
        file_name = configs.get("file_name", None)

        return cls(
            file_content=file_content,
            file_name=file_name,
            mime_type=MimeType(mime_type),
            chat_model=chat_model
        )

    @staticmethod
    def _generate_csv_prompt(file_name, warnings_string: Optional[str] = None):
        warning_section = ""
        if warnings_string:
            warning_section = (
                f"\n**ALWAYS Note the user is they exist. Warning(s) while reading the CSV:**\n"
                f"{warnings_string}\n"
                "These warnings were generated while loading the CSV file. "
                "They may indicate malformed rows, missing values, or other data issues. "
                "Please take them into account when analyzing the data.\n"
            )

        return f"""A CSV file named '{file_name}' has been uploaded by the user,
    and it has already been loaded into a Pandas DataFrame called `df`.
    {warning_section}
     - You may ask clarifying questions if something is unclear.
     - In your explanations or final answers, refer to the CSV by its file name '{file_name}' rather than `df`.
    Remember:
    1) The DataFrame variable is `df`.
    2) The file name is '{file_name}'.
    """
