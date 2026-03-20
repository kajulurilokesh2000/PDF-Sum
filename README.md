# PDF Summarizer API

A FastAPI backend service that extracts text from PDF files and generates AI-powered summaries using OpenAI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_actual_api_key
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `POST /api/summarize` - Upload PDF and get summary

## Usage Example

```bash
curl -X POST "http://localhost:8000/api/summarize" \
  -F "file=@document.pdf"
```

## Response Format

```json
{
  "filename": "document.pdf",
  "summary": "Summary:\n...\n\nKey Points:\n- point 1\n- point 2"
}
```
