from unidoc_agent.base_tool import BaseTool
import fitz

class PDFTool(BaseTool):
    def can_handle(self, file_path, mime_type):
        return mime_type == 'application/pdf'

    def extract_content(self, file_path):
        text = ''
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text