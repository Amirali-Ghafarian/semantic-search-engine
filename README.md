# semantic-search-engine

A semantic PDF search engine built with FastAPI, `sentence-transformers`, and FAISS.

## MVP scope

- Upload a PDF file
- Extract and chunk text page by page
- Generate semantic embeddings
- Index chunks with FAISS
- Search words or phrases against uploaded documents
- Return ranked results with page references

## Project structure

```text
app/
	api/          FastAPI app and route handlers
	core/         Configuration and logging
	embeddings/   Embedding model wrapper
	indexing/     Vector index and metadata persistence
	ingestion/    PDF loading and chunking
	retrieval/    Search strategies
	schemas/      Request and response models
	services/     Application orchestration layer
data/
	raw/          Uploaded PDFs
	processed/    Future preprocessed artifacts
	indices/      Persisted FAISS index and metadata
tests/          Unit and API smoke tests
```

## Local development

1. Create and activate a virtual environment.
2. Install dependencies with `uv sync --dev`
3. Start the API with `uv run uvicorn app.api.main:app --reload`
4. Open the interactive API docs at `http://127.0.0.1:8000/docs`

Recommended local Python version: 3.11 or 3.12 for the smoothest compatibility with `faiss-cpu` and `sentence-transformers`.

## Docker

Build and run with Docker:

1. `docker build -t semantic-search-engine .`
2. `docker run -p 8000:8000 semantic-search-engine`

Or run with Docker Compose:

1. `docker compose up --build`