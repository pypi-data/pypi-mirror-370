from typing import Dict, Any, Optional

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.vision.image_tool import ImageTool


class VisionToolkit(BaseToolkit):
    image_content: Optional[Any] = None
    chat_model: Optional[Any] = None

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        return ToolKit(
            toolkit=ToolSet.VISION.value,
            tools=[
                Tool(name='image_tool', label='Image Recognition', user_description="Image Recognition"),
            ]
        ).model_dump()

    def get_tools(self):
        return [
            ImageTool(image_content=self.image_content, chat_model=self.chat_model)
        ]

    @classmethod
    def get_toolkit(cls,
                    configs: Dict[str, Any],
                    chat_model: Optional[Any] = None):
        image_content = configs.get("image_content", None)
        return VisionToolkit(image_content=image_content, chat_model=chat_model)
