# UniversalDocAgent (`unidoc_agent`)

UniversalDocAgent is a Python package designed to intelligently detect document types and automatically extract or summarize their contents using a set of specialized tools. It supports a wide range of file types such as PDFs, Word documents, emails, source code, Excel files, XML, OCR-recognizable images, and plain text.

You can optionally integrate with an LLM backend like **Ollama** to generate summaries and maintain conversation history across sessions.

---

## 🚧 Installation

```bash
pip install .
```

Run this from the root directory of your cloned project or package.

---

## 📂 Supported Document Types

| File Type          | Handled By |
|--------------------|------------|
| `.pdf`             | PDFTool    |
| `.docx`            | WordTool   |
| `.txt`             | TextTool   |
| `.py`, `.js`, etc. | CodeTool   |
| `.eml`             | EmailTool  |
| `.xlsx`            | ExcelTool  |
| `.jpg`, `.png`, etc.| OCRTool   |
| `.xml`             | XMLTool    |

---

## 🚀 Usage Examples

### 1. Extracting Content

```python
from unidoc_agent.agent import read_document

file_path = "sample.pdf"
content = read_document(file_path)
print(content)
```

### 2. Summarizing Content

```python
summary = read_document("example.docx", summarize=True)
print(summary)
```

---

## 🧠 Advanced: Use Ollama LLM Backend

### Custom LLM model or session

```python
from unidoc_agent.agent import UniversalDocAgent
from unidoc_agent.agent import tools

agent = UniversalDocAgent(tools=tools, llm_backend="ollama")
summary = agent.summarize_content("report.txt")
print(summary)
```

---

## 💬 Conversation History with `OllamaClient`

The `OllamaClient` class is used internally to manage conversation context for summarization.

- **Caching**: Stores conversation history locally in `~/.unidoc_ollama_cache/{model}_{session_id}.json`
- **Session Management**: Custom session IDs let you manage multiple user contexts

### Clearing History

```python
from unidoc_agent.ollama_client import OllamaClient

client = OllamaClient(session_id="user123")
client.clear_history()
```

---

## 🔧 API Reference

### `read_document(file_path, summarize=False)`
- `file_path`: Path to the input document
- `summarize`: If `True`, returns a summary via LLM; else returns extracted content

### `UniversalDocAgent`
- `extract_content(file_path)`: Extracts raw content
- `summarize_content(file_path)`: Summarizes content using the selected tool + LLM

---

## 🔮 Tests

Make sure you have `pytest` or `unittest` installed:

```bash
pytest
```

Or:

```bash
python -m unittest discover tests/
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 📊 Use Cases

- ✉️ **Email Parsing** – Automatically extract the body of `.eml` files and summarize them.
- 📄 **Document Summary** – Get concise summaries of long reports, manuals, or meeting notes.
- 📈 **Spreadsheet Reader** – Read `.xlsx` Excel files and extract tables or data grids.
- 🔧 **OCR Scanning** – Use OCRTool to read text from images (e.g., scanned receipts).
- 📁 **Source Code Insight** – Extract and analyze comments or logic from `.py` or `.js` files.
- 📖 **Multi-format Aggregation** – Use the same interface (`read_document`) for any supported format.

---

## 🚀 Contributing

Pull requests are welcome. Please open issues for bugs or feature requests.

---

## ✨ Acknowledgements

Thanks to OpenAI, Ollama, and the open-source contributors whose tools helped build this module.
