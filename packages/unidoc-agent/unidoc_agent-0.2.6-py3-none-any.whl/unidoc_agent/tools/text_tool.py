from unidoc_agent.base_tool import BaseTool

class TextTool(BaseTool):
    def can_handle(self, file_path, mime_type):
        return mime_type == 'text/plain'

    def extract_content(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()