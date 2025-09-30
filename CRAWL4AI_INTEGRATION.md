# Crawl4AI Frontend-Backend Integration

This integration connects the Orion frontend to the backend for web scraping using Crawl4AI.

## How It Works

1. **Frontend Input**: User enters a URL in the Knowledge Management panel
2. **Backend Processing**: FastAPI calls `/api/v1/admin/crawl4ai-scrape` endpoint  
3. **Subprocess Execution**: Backend runs `insert_docs.py` as a subprocess with the URL
4. **Real-time Updates**: Frontend polls the status endpoint for progress updates
5. **Completion**: Results are displayed showing chunks processed and stored in ChromaDB

## API Endpoints

### POST `/api/v1/admin/crawl4ai-scrape`
Start web scraping for a URL.

**Request Body:**
```json
{
  "url": "https://example.com",
  "description": "Example Website",
  "collection_name": "docs",
  "max_depth": 3,
  "chunk_size": 1000
}
```

**Response:**
```json
{
  "task_id": "uuid-here",
  "status": "started",
  "message": "Crawl4AI scraping started for https://example.com",
  "url": "https://example.com",
  "collection_name": "docs",
  "estimated_completion": "2024-03-15T16:30:00Z"
}
```

### GET `/api/v1/admin/crawl4ai-status/{task_id}`
Get the status of a scraping task.

**Response:**
```json
{
  "task_id": "uuid-here",
  "status": "processing|completed|failed",
  "progress": 75.0,
  "url": "https://example.com",
  "collection_name": "docs",
  "chunks_processed": 150,
  "created_at": "2024-03-15T16:00:00Z",
  "updated_at": "2024-03-15T16:15:00Z",
  "result": null,
  "error_message": null
}
```

## Frontend Features

- **Real-time Status**: Live progress updates with polling
- **Error Handling**: Retry failed scraping attempts
- **Visual Feedback**: Progress bars and status indicators
- **Clean UI**: No hardcoded URLs, user-driven input

## Setup Instructions

### Backend
1. Ensure `requirements.txt` is installed with Crawl4AI dependencies
2. Start the FastAPI server: `uvicorn app.main:app --reload`
3. Test the setup: `GET /api/v1/admin/crawl4ai-test`

### Frontend  
1. Copy `.env.example` to `.env` and configure API URL
2. Start the development server: `npm run dev`
3. Navigate to Admin Dashboard > Knowledge Management
4. Add URLs for scraping

## File Structure

```
Orion-backend/
├── workers/crawl4AI-agent-v2/
│   ├── insert_docs.py          # Main scraping script
│   ├── utils.py               # ChromaDB utilities
│   └── rag_agent.py           # RAG agent
├── app/api/v1/admin.py        # API endpoints
└── models/admin_models.py     # Pydantic models

Orion-frontend/
├── src/components/admin/
│   └── knowledge-management.tsx   # UI component
├── .env                           # Environment config
└── .env.example                   # Environment template
```

## Key Features Implemented

✅ **No Hardcoded URLs**: All URLs come from user input  
✅ **Subprocess Integration**: Uses `asyncio.create_subprocess_exec`  
✅ **Real-time Polling**: Frontend polls backend for status updates  
✅ **Error Handling**: Proper error messages and retry functionality  
✅ **Progress Tracking**: Visual progress bars and status indicators  
✅ **Background Tasks**: Non-blocking scraping using FastAPI BackgroundTasks  
✅ **Clean UI**: Professional interface with toast notifications

## Testing

1. Start both frontend and backend servers
2. Go to Admin Dashboard > Knowledge Management  
3. Enter a URL (e.g., https://docs.python.org)
4. Watch real-time progress updates
5. Check ChromaDB collection for scraped content

## Troubleshooting

- **subprocess not found**: Ensure Python is in PATH
- **insert_docs.py missing**: Check file paths in admin.py
- **CORS errors**: Verify API_BASE_URL in frontend .env
- **Polling issues**: Check network connectivity and API endpoints