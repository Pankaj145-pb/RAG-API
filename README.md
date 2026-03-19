# RAG API

A Retrieval-Augmented Generation (RAG) API built with FastAPI that allows you to query embedded documents using natural language. This repository demonstrates how to store embeddings in ChromaDB and run model inference — now updated to use the OpenAI API for embeddings and chat/completion.
# RAG API

A Retrieval-Augmented Generation (RAG) API built with FastAPI that allows you to query embedded documents using natural language. This project uses ChromaDB for vector storage and Ollama for language model inference.

## Prerequisites

- **Python 3.8+** installed
- An OpenAI API key with access to embeddings and chat models
- `ollama` is no longer required for the OpenAI workflow

## Install dependencies

Run:

```bash
pip install -r requirements.txt
# or, if you prefer installing manually:
pip install fastapi chromadb openai uvicorn
```

If you don't have a `requirements.txt` file, create one with these lines:

```
fastapi
chromadb
openai
uvicorn
```

**Set your OpenAI API key (PowerShell)**

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

On macOS / Linux (bash/zsh):

```bash
export OPENAI_API_KEY="sk-..."
```

**Embedding documents**

- `embed.py` now uses OpenAI embeddings. To embed `k8s.txt` and store it in ChromaDB run:

```bash
python embed.py
```

- Behind the scenes `embed.py` calls OpenAI's Embeddings API (`text-embedding-3-small`) and stores the vector in the local ChromaDB at `./db`.

**Running the API**

- Start the FastAPI server:

```bash
uvicorn app:app --reload
```

- Endpoints provided by the app:

- **POST** `/add` — Add a new document to the knowledge base. The server will create an OpenAI embedding for the text and store it in ChromaDB. Example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/add" -H "Content-Type: application/json" -d '{"text":"My new knowledge"}'
```

- **POST** `/query` — Query the knowledge base. The server performs a Chroma nearest-neighbor search, then sends the found context to the OpenAI Chat API to generate a concise answer. Example:

```bash
curl -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d '{"q":"What is Kubernetes?"}'
```

**Files to inspect**

- The embedding script: [embed.py](embed.py)
- The API server: [app.py](app.py)

**Notes & tips**

- Model choices:
  - Embeddings: `text-embedding-3-small` is used by default. You can change this in `embed.py` and `app.py` when creating embeddings.
  - Chat/Completion: the current code uses `gpt-4o-mini` for concise answers; change the `model` in `app.py` to another compatible OpenAI model if desired.

- ChromaDB storage:
  - The Chroma DB files are stored under `./db` (see the `db/` folder). Keep this directory if you want to preserve embeddings between runs.

- API key security:
  - Do not commit your `OPENAI_API_KEY` to source control. Use environment variables or a secrets manager in production.

**Rollback to Ollama (if needed)**

If you prefer to use Ollama/TinyLlama again, the previous implementation used `ollama.generate(model="tinyllama", ...)` in `app.py` and `ollama.embed` in earlier embedding code. That approach required an `ollama` daemon and a downloaded TinyLlama model.

**Next steps**

- Run `python embed.py` to store embeddings, then start the server with `uvicorn app:app --reload` and test the endpoints.
- If you want, I can also add a `requirements.txt`, a `.env` example, or a short test script that exercises `/add` and `/query` automatically.

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