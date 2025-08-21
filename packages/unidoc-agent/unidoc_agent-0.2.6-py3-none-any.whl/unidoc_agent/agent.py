from .tools.pdf_tool import PDFTool
from .tools.word_tool import DocxTool
from .tools.text_tool import TextTool
from .tools.code_tool import CodeTool
from .tools.email_tool import EmailTool
from .tools.excel_tool import ExcelTool
from .tools.ocr_tool import OCRTool
from .tools.xml_tool import XMLTool
import mimetypes

# Initialize MIME types for supported file types
def init_mime_types():
    mime_mappings = {
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.js': 'text/javascript',
        '.py': 'text/x-python',
        '.java': 'text/x-java-source',
        '.cpp': 'text/x-c++src',
        '.c': 'text/x-csrc',
        '.cs': 'text/x-csharp',
        '.go': 'text/x-go',
        '.rb': 'text/x-ruby',
        '.php': 'text/x-php',
        '.ts': 'text/typescript',
        '.html': 'text/html',
        '.css': 'text/css',
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.xml': 'application/xml',
        '.eml': 'message/rfc822'
    }
    for ext, mime in mime_mappings.items():
        mimetypes.add_type(mime, ext)

# Call init_mime_types once at module level
init_mime_types()

tools = [PDFTool(), DocxTool(), TextTool(), CodeTool(), EmailTool(), ExcelTool(), OCRTool(), XMLTool()]

class UniversalDocAgent:
    def __init__(self, tools, llm_backend='ollama', session_id='12345'):
        self.tools = tools
        self.llm_backend = llm_backend
        self.session_id = session_id

    def detect_tool(self, file_path):
        mime, _ = mimetypes.guess_type(file_path)
        for tool in self.tools:
            if tool.can_handle(file_path, mime):
                return tool
        # Fallback to CodeTool for text-like or unrecognized files
        if mime is None or mime.startswith(('text/', 'application/')) or file_path.lower().endswith(('.js', '.py', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.ts', '.html', '.css', '.txt')):
            return CodeTool()
        raise ValueError(f"No suitable tool found for {file_path}")

    def extract_content(self, file_path):
        tool = self.detect_tool(file_path)
        return tool.extract_content(file_path)

    def summarize_content(self, file_path):
        content = self.extract_content(file_path)
        if self.llm_backend == 'ollama':
            from .ollama_client import OllamaClient
            client = OllamaClient(session_id=self.session_id)
            return client.chat(f"Please summarize the following content:\n\n{content}")
        else:
            return f"Summary: This file contains {len(content.split())} words."

def read_document(file_path, summarize=False, llm_backend='ollama', session_id='default_user'):
    agent = UniversalDocAgent(tools, llm_backend=llm_backend, session_id=session_id)
    return agent.summarize_content(file_path) if summarize else agent.extract_content(file_path)