import base64
from typing import Type, Optional, Any

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.vision.tool_vars import IMAGE_TOOL

VISION_PROMPT = """
  Analyze and provide a detailed description of the image.
  If the image contains text, transcribe the text as well.
  
  Expected output:
  <description>
  Transcribed text: <transcribed_text>
"""

MAX_TOKENS = 1_000


class Input(BaseModel):
    query: str = Field(description="Detailed user query for image recognition", )


class ImageTool(CodeMieTool):
    """ Calls gpt-vision to interpret and transcribe image contents """
    args_schema: Type[BaseModel] = Input

    name: str = IMAGE_TOOL.name
    label: str = IMAGE_TOOL.label
    description: str = IMAGE_TOOL.description
    image_content: Optional[Any] = None
    chat_model: Optional[Any] = Field(exclude=True)

    def execute(self, query: str, **kwargs):
        if self.image_content is None:
            raise ValueError("Image content is not set")
        return self.generate()

    def generate(self) -> str:
        result = self.chat_model.invoke(
            [
                HumanMessage(content=[
                    {
                        "type": "text",
                        "text": VISION_PROMPT
                    },
                    {
                        "type": "image",
                        "source_type": "base64",
                        "data": self.base64_content(),
                        "mime_type": "image/png",
                    },
                ])
            ],
            max_tokens=MAX_TOKENS
        )

        return result.content

    def base64_content(self) -> str:
        return base64.b64encode(self.image_content).decode("utf-8")
