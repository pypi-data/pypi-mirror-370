from typing import Type, Any, Optional
import io

import chardet
from pydantic import BaseModel, Field
from markitdown import MarkItDown

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.file_analysis.tool_vars import FILE_ANALYSIS_TOOL

class FileAnalysisToolInput(BaseModel):
    file_name: str = Field(description="Name of the file you are trying to analyze.")

class FileAnalysisTool(CodeMieTool):
    """ Tool for working with and analyzing file contents. """
    args_schema: Optional[Type[BaseModel]] = FileAnalysisToolInput
    name: str = FILE_ANALYSIS_TOOL.name
    label: str = FILE_ANALYSIS_TOOL.label
    description: str = FILE_ANALYSIS_TOOL.description
    file_content: Any = Field(exclude=True)

    def _fallback_decode_text_file(self, file_name: str, original_exception: Exception = None) -> str:
        """
        Private fallback method to decode text files when markitdown fails
        :param file_name: Name of the file
        :param original_exception: The original exception from markitdown (if any)
    
        :return: file content as string or error message
        """
        if file_name.lower().endswith(('.txt', '.md', '.py', '.java', '.js', '.html', '.css')):
            try:
                bytes_data = self.bytes_content()
                encoding_info = chardet.detect(bytes_data)
                encoding = encoding_info.get('encoding') if encoding_info and encoding_info.get('encoding') else 'utf-8'
    
                try:
                    data = bytes_data.decode(encoding)
                except UnicodeDecodeError:
                    data = bytes_data.decode('utf-8', errors='replace')
    
                return str(data)
            except Exception as inner_e:
                return f"Failed to decode file: {str(inner_e)}"
    
        error_msg = "File type not supported for direct decoding"
        if original_exception:
            error_msg += f". Original error: {str(original_exception)}"
        return error_msg
    
    def execute(self, file_name: str):
        try:
            # Use markitdown library for file conversion
            md = MarkItDown(enable_plugins=True)
            # Create a file-like object from bytes content
            binary_content = io.BytesIO(self.bytes_content())
            result = md.convert(binary_content)
            return result.text_content
        except FileNotFoundError as e:
            # Handle the case when a file is not found
            return f"File not found: {str(e)}"
        except Exception as e:
            # Fallback to direct decoding for text files if markitdown fails
            return self._fallback_decode_text_file(file_name, original_exception=e)

    def bytes_content(self) -> bytes:
        """
        Returns the content of the file as bytes
        """
        if self.file_content is None:
            raise ValueError("File content is not set")
        if isinstance(self.file_content, bytes):
            return self.file_content

        return self.file_content.encode('utf-8', errors='replace')