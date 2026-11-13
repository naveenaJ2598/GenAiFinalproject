<<<<<<< HEAD
# LinguaMate AI

A local-first English learning and PDF question-answering app.

## Features
- English Coach: sentence correction, Tamil explanation, natural alternative and vocabulary.
- PDF Assistant: upload a text-based PDF and ask questions about its content.
- Streamlit frontend and separate Python backend modules.
- Ollama local model integration.

## Requirements
- Python 3.11 or newer
- Ollama installed and running
- Ollama model: `qwen2.5:1.5b`

## Setup
1. Extract the ZIP file.
2. Open the `LinguaMateAI` folder.
3. Make sure Ollama is running.
4. Open `run.bat` (double-click), or run these commands in the project folder:

```bash
python -m pip install -r requirements.txt
ollama pull qwen2.5:1.5b
python -m streamlit run frontend/app.py
```

5. Streamlit will show a local URL, usually `http://localhost:8501`.

## Folder structure

```text
LinguaMateAI/
├── frontend/
│   └── app.py
├── backend/
│   ├── __init__.py
│   ├── logic.py
│   └── rag.py
├── documents/
├── requirements.txt
├── run.bat
└── README.md
```

## Notes
- PDF extraction currently supports selectable text PDFs. Scanned PDFs need OCR, which is not included.
- The English Coach uses Python rules for a few known examples and Ollama for other sentences. Local LLM Tamil quality can vary.
- PDF retrieval is a lightweight keyword-based RAG implementation, not embedding-based semantic search.
=======
# GenAiFinalproject
>>>>>>> ddbab8ed07f50139dd8adf077f31677b47732807
