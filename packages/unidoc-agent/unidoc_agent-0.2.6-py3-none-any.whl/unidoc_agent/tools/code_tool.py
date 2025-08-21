from unidoc_agent.base_tool import BaseTool

class CodeTool(BaseTool):
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        # Handle common code file extensions explicitly
        code_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.ts'}
        return (
            file_path.lower().endswith(tuple(code_extensions)) or
            mime_type and (mime_type.startswith('text/') or mime_type == 'application/javascript')
        )

    def extract_content(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            return f"Could not decode content from code file: {file_path}"