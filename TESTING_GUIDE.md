# Orion Backend Testing Guide

This guide provides step-by-step instructions for testing the Orion backend system.

## Prerequisites

1. **Python Environment**: Ensure Python 3.8+ is installed
2. **Dependencies**: Install all required packages
3. **Environment Variables**: Configure the .env file with your settings

## Step 1: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

Edit the `.env` file and update the following critical settings:

```env
# Database (if using PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/orion_db

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# OpenAI API (for RAG functionality)
OPENAI_API_KEY=your-actual-openai-api-key

# JWT Secret (change from default)
JWT_SECRET_KEY=your-secure-secret-key-here
```

## Step 3: Start the FastAPI Server

```bash
# Start the development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server should start and display:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

## Step 4: Test API Endpoints

### 4.1 Health Check Endpoints

```bash
# Test root endpoint
curl http://127.0.0.1:8000/

# Expected response:
# {"message":"Orion Backend API is running","version":"1.0.0"}

# Test health endpoint
curl http://127.0.0.1:8000/health

# Expected response:
# {"status":"healthy","service":"orion-backend","version":"1.0.0"}
```

### 4.2 API Documentation

Visit these URLs in your browser:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 4.3 Admin Endpoints

```bash
# Test admin login endpoint
curl -X POST http://127.0.0.1:8000/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# Test admin dashboard (requires authentication)
curl -X GET http://127.0.0.1:8000/api/v1/admin/dashboard \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4.4 Chat Endpoints

```bash
# Test chat endpoint
curl -X POST http://127.0.0.1:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, what can you tell me about the campus?"}'
```

## Step 5: Test Background Tasks (Celery)

### 5.1 Start Redis Server
```bash
# On Windows (if Redis is installed)
redis-server

# On Linux/Mac
redis-server
```

### 5.2 Start Celery Worker
```bash
# In a new terminal window
celery -A workers.celery_app worker --loglevel=info
```

### 5.3 Test Celery Tasks
```bash
# Test a background task
python -c "
from workers.tasks import process_document_ingestion
result = process_document_ingestion.delay('test-document.pdf')
print(f'Task ID: {result.id}')
print(f'Task Status: {result.status}')
"
```

## Step 6: Test Individual Components

### 6.1 Test Configuration Loading
```bash
python -c "
from core.config import get_settings
settings = get_settings()
print(f'Debug: {settings.debug}')
print(f'Environment: {settings.environment}')
print('✓ Configuration loaded successfully')
"
```

### 6.2 Test Security Functions
```bash
python -c "
from core.security import create_access_token, get_password_hash, verify_password
token = create_access_token({'sub': 'test_user'})
print(f'JWT Token: {token[:50]}...')
hash_pwd = get_password_hash('test123')
print(f'Password Hash: {hash_pwd[:50]}...')
print('✓ Security functions working')
"
```

### 6.3 Test Pydantic Models
```bash
python -c "
from models.chat_models import ChatRequest, ChatResponse
from models.admin_models import LoginRequest
from models.user_models import User

# Test ChatRequest model
chat_req = ChatRequest(message='Test message')
print(f'Chat Request: {chat_req.message}')

# Test LoginRequest model
login_req = LoginRequest(username='admin', password='test')
print(f'Login Request: {login_req.username}')
print('✓ All models working correctly')
"
```

### 6.4 Test Services
```bash
python -c "
from services.rag_service import RAGService
from services.ingestion_service import IngestionService

print('✓ Services imported successfully')
# Note: Full service testing requires proper configuration
"
```

## Step 7: Integration Testing

### 7.1 Full Workflow Test
```bash
# 1. Start the server
uvicorn app.main:app --reload &

# 2. Wait for server to start
sleep 3

# 3. Test complete workflow
curl -X POST http://127.0.0.1:8000/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' > login_response.json

# 4. Extract token and test authenticated endpoint
# (This requires jq or manual token extraction)
```

## Step 8: Performance Testing

### 8.1 Load Testing with curl
```bash
# Simple load test
for i in {1..10}; do
  curl -s http://127.0.0.1:8000/health &
done
wait
echo "Load test completed"
```

### 8.2 Using Apache Bench (if installed)
```bash
# Test 100 requests with 10 concurrent connections
ab -n 100 -c 10 http://127.0.0.1:8000/health
```

## Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Port Already in Use**: Change the port or kill existing processes
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # Linux/Mac
   lsof -ti:8000 | xargs kill -9
   ```

3. **Environment Variables**: Ensure .env file is properly configured

4. **Database Connection**: Verify database is running and credentials are correct

5. **Redis Connection**: Ensure Redis server is running for Celery tasks

## Expected Test Results

✅ **Server Startup**: No errors, server runs on http://127.0.0.1:8000
✅ **Health Endpoints**: Return proper JSON responses
✅ **API Documentation**: Accessible at /docs and /redoc
✅ **Module Imports**: All modules import without errors
✅ **Configuration**: Environment variables load correctly
✅ **Security**: JWT tokens and password hashing work
✅ **Models**: Pydantic models validate correctly
✅ **Background Tasks**: Celery workers process tasks

## Next Steps

After successful testing:
1. Set up a proper database (PostgreSQL)
2. Configure Redis for production
3. Add your OpenAI API key for RAG functionality
4. Implement proper logging and monitoring
5. Set up CI/CD pipeline for automated testing
