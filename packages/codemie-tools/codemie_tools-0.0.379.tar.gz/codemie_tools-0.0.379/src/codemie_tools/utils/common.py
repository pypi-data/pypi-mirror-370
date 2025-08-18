from pydantic import ValidationError

from codemie_tools.base.codemie_tool import logger


def humanize_error(error: Exception) -> str:
    """
    If an error is a Pyndatic ValidationError, return a human-readable string
    Otherwise, return the string representation of the error.
    """
    if not isinstance(error, ValidationError):
        return str(error)
      
    try:
      return ", ".join([
        f"{_format_pydantic_validation_loc(item['loc'])}: {item['msg'].lower()}"
        for item in error.errors()
      ]).capitalize()
    except Exception:
        logger.error("Error formatting Pydantic ValidationError", exc_info=True)
        return str(error)
    
def _format_pydantic_validation_loc(items): 
  """Humanize the location field of a Pydantic validation error"""
  return ".".join(str(loc) for loc in items)