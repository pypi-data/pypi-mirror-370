from unidoc_agent.base_tool import BaseTool
from email import policy
from email.parser import BytesParser

class EmailTool(BaseTool):
    def can_handle(self, file_path, mime_type):
        return file_path.endswith('.eml')

    def extract_content(self, file_path):
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        return msg.get_body(preferencelist=('plain')).get_content()