from unidoc_agent.base_tool import BaseTool
import openpyxl
import json

class ExcelTool(BaseTool):
    def can_handle(self, file_path, mime_type):
        return file_path.endswith(('.xlsx', '.xls'))

    def extract_content(self, file_path):
        wb = openpyxl.load_workbook(file_path, data_only=True)
        structured_data = {}

        for sheet in wb:
            rows = list(sheet.iter_rows(values_only=True))
            sheet_data = []

            if not rows:
                structured_data[sheet.title] = []
                continue

            raw_headers = rows[0]
            non_empty_count = sum(1 for h in raw_headers if h)
            unique_headers = set(h for h in raw_headers if h)
            is_valid_header = non_empty_count >= len(raw_headers) // 2 and len(unique_headers) == non_empty_count

            if is_valid_header:
                headers = [str(h).strip() if h else f"Column{i+1}" for i, h in enumerate(raw_headers)]

                for row in rows[1:]:
                    row_dict = {headers[i]: row[i] for i in range(len(headers))}
                    if any(v is not None for v in row_dict.values()):
                        sheet_data.append(row_dict)

            else:
                for row in rows:
                    row_dict = {f"Column{i+1}": v for i, v in enumerate(row) if v is not None}
                    if row_dict:
                        sheet_data.append(row_dict)

            structured_data[sheet.title] = sheet_data

        return json.dumps(structured_data, indent=2)