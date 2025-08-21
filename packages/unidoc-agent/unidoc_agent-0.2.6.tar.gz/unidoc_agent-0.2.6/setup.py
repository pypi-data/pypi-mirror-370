from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="unidoc_agent",
    version="0.2.6", # 🚨 Bump the version when re-uploading
    packages=find_packages(),
    install_requires=[
        "python-docx",
        "PyMuPDF",
        "pytesseract",
        "pandas",
        "openpyxl",
        "ollama",
    ],
    author="Vedansh Bhatnagar",
    description="Universal Document Agent for extracting and analyzing various documents with Ollama support.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Ensures PyPI renders it correctly
    keywords=["document", "pdf", "docx", "text", "code", "extract", "ollama", "chatbot"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    license="MIT",
)