from unidoc_agent.base_tool import BaseTool
import xml.etree.ElementTree as ET

class XMLTool(BaseTool):
    def can_handle(self, file_path, mime_type):
        return file_path.endswith('.xml')

    def extract_content(self, file_path):
        tree = ET.parse(file_path)
        return ET.tostring(tree.getroot(), encoding='unicode')