from unidoc_agent.base_tool import BaseTool
import pytesseract
from PIL import Image

class OCRTool(BaseTool):
    def can_handle(self, file_path, mime_type):
        return mime_type and mime_type.startswith('image')

    def extract_content(self, file_path):
        return pytesseract.image_to_string(Image.open(file_path))