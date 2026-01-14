# RAG API

A Retrieval-Augmented Generation (RAG) API built with FastAPI that allows you to query embedded documents using natural language. This project uses ChromaDB for vector storage and Ollama for language model inference.

## Features

- **Document Embedding**: Store and index documents for semantic search
- **Natural Language Queries**: Ask questions about your documents in plain English
- **RESTful API**: Simple HTTP endpoints for adding content and querying
- **Persistent Storage**: Documents are stored in a local ChromaDB database

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- TinyLlama model pulled in Ollama (`ollama pull tinyllama`)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd "RAG API"
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install fastapi chromadb ollama uvicorn
   ```

4. Ensure Ollama is running and has the TinyLlama model:
   ```bash
   ollama serve
   ollama pull tinyllama
   ```

## Usage

### Running the API

Start the FastAPI server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Add Knowledge
**POST** `/add`

Add new content to the knowledge base.

**Request Body:**
```json
{
  "text": "Your document content here"
}
```

**Response:**
```json
{
  "status": "Success",
  "message": "Content added to knowledge base",
  "id": "unique-document-id"
}
```

#### Query Knowledge Base
**POST** `/query`

Ask questions about the stored documents.

**Request Body:**
```json
{
  "q": "What is Kubernetes?"
}
```

**Response:**
```json
{
  "answer": "Kubernetes is a container orchestration platform used to manage containers at scale."
}
```

### Initial Data Setup

The project comes with sample Kubernetes documentation. To embed it:

```bash
python embed.py
```

This will read `k8s.txt` and store its embeddings in the ChromaDB database.

## Project Structure

```
RAG API/
├── app.py          # Main FastAPI application
├── embed.py        # Script to embed initial documents
├── k8s.txt         # Sample Kubernetes documentation
├── db/             # ChromaDB persistent storage (auto-generated)
├── venv/           # Virtual environment (auto-generated)
└── README.md       # This file
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` to see the interactive API documentation provided by FastAPI.

## Development

### Adding More Documents

You can add more documents by:

1. Creating text files with your content
2. Modifying `embed.py` to read and embed them
3. Or using the `/add` endpoint to add content programmatically

### Changing the LLM Model

To use a different Ollama model, update the model name in `app.py`:

```python
answer = ollama.generate(
    model="your-model-name",  # Change this
    prompt=f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer clearly and concisely:"
)
```

## License

This project is open source. Feel free to use and modify as needed.