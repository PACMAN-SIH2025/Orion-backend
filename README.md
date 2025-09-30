# Orion Backend API

A RAG-powered educational assistant backend built with FastAPI, designed to provide intelligent campus information and support to students through natural language interactions.

## 🚀 Features

- **RAG-Powered Chat**: Intelligent question-answering using Retrieval-Augmented Generation
- **Document Ingestion**: Automated processing of PDFs, web content, and documents
- **Admin Dashboard**: Comprehensive admin interface for content management
- **Background Processing**: Asynchronous document processing with Celery
- **JWT Authentication**: Secure admin authentication and authorization
- **Vector Search**: Efficient semantic search using embeddings
- **RESTful API**: Well-documented FastAPI endpoints
- **Real-time Monitoring**: Built-in health checks and logging

## 🏗️ Architecture

```
Orion Backend
├── FastAPI Application (app/)
├── Core Services (core/)
├── Data Models (models/)
├── Business Logic (services/)
└── Background Workers (workers/)
```

### Components

- **FastAPI App**: Main application with middleware and routing
- **RAG Service**: Core retrieval-augmented generation pipeline
- **Ingestion Service**: Document processing and chunking
- **Admin API**: Authentication and content management
- **Chat API**: Public student query interface
- **Celery Workers**: Asynchronous background tasks

## 📋 Prerequisites

- Python 3.8+
- Redis (for Celery background tasks)
- PostgreSQL (recommended for production)
- Google Gemini API key (for embeddings and chat completion)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PACMAN-SIH2025/Orion-backend.git
cd Orion-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

**For Production Setup:**
```bash
pip install -r requirements.txt
```

**For Development:**
```bash
pip install -r requirements-dev.txt
```

**For All Features (ML, Demos, etc.):**
```bash
pip install -r requirements-optional.txt
```

See [REQUIREMENTS_GUIDE.md](REQUIREMENTS_GUIDE.md) for detailed dependency information.

### 4. Environment Configuration

Copy and configure the environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Application Settings
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/orion_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key-here

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-here
```

## 🚀 Quick Start

### 1. Start the Application

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Access API Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 3. Health Check

```bash
curl http://127.0.0.1:8000/health
```

## 📚 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/api/v1/chat/` | Student chat queries |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/admin/login` | Admin authentication |
| GET | `/api/v1/admin/dashboard` | Admin dashboard |
| POST | `/api/v1/admin/ingest` | Document ingestion |
| GET | `/api/v1/admin/logs` | System logs |

## 🔧 Background Tasks

### Start Celery Worker

```bash
celery -A workers.celery_app worker --loglevel=info
```

### Start Celery Flower (Monitoring)

```bash
celery -A workers.celery_app flower
```

Access Flower dashboard at: http://localhost:5555

## 🧪 Testing

### Run Basic Tests

```bash
# Test all imports
python -c "import app.main; print('✓ All modules imported successfully')"

# Test configuration
python -c "from core.config import get_settings; print('✓ Configuration loaded')"

# Test security
python -c "from core.security import create_access_token; print('✓ Security working')"
```

### Comprehensive Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing instructions.

## 📁 Project Structure

```
Orion-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── admin.py        # Admin endpoints
│           └── chat.py         # Chat endpoints
├── core/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   └── security.py            # Authentication & security
├── models/
│   ├── __init__.py
│   ├── admin_models.py        # Admin API models
│   ├── chat_models.py         # Chat API models
│   └── user_models.py         # User data models
├── services/
│   ├── __init__.py
│   ├── ingestion_service.py   # Document processing
│   └── rag_service.py         # RAG pipeline
├── workers/
│   ├── __init__.py
│   ├── celery_app.py          # Celery configuration
│   └── tasks.py               # Background tasks
├── .env                       # Environment variables
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies  
├── requirements-optional.txt  # Optional features (ML, demos)
├── README.md                  # This file
├── REQUIREMENTS_GUIDE.md      # Dependency management guide
└── TESTING_GUIDE.md          # Testing instructions
```

## 🔒 Security

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **CORS Protection**: Configurable CORS middleware
- **Rate Limiting**: Built-in request rate limiting
- **Input Validation**: Pydantic model validation

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | Application secret key | Required |
| `DATABASE_URL` | Database connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `JWT_SECRET_KEY` | JWT signing key | Required |

## 📊 Monitoring & Logging

### Health Endpoints

- `/health` - Basic health check
- `/` - Root endpoint with version info

### Logging

Logs are configured using Python's logging module with:
- Console output for development
- File output for production
- Structured JSON logging support

### Monitoring Tools

- **Flower**: Celery task monitoring
- **FastAPI Docs**: Built-in API documentation
- **Health Checks**: Automated health monitoring

## 🚀 Deployment

### Docker Deployment

``dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Database**: Use PostgreSQL for production
2. **Redis**: Configure Redis persistence
3. **Environment**: Set `DEBUG=false`
4. **Security**: Use strong secret keys
5. **Monitoring**: Set up proper logging and monitoring
6. **Scaling**: Consider horizontal scaling with load balancers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for all functions
- Document all public APIs
- Write comprehensive tests

### Git Workflow

- Use conventional commit messages
- Keep commits atomic and focused
- Write descriptive commit messages
- Use feature branches for development

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Port Conflicts**: Change port or kill existing processes
3. **Database Connection**: Verify database credentials
4. **Redis Connection**: Ensure Redis server is running
5. **API Key Issues**: Verify OpenAI API key is valid

### Debug Mode

Enable debug mode for detailed error messages:

```env
DEBUG=true
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- OpenAI for powerful language models
- Celery for background task processing
- The open-source community for amazing tools

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing help
- Review the API documentation at `/docs`

---

**Orion Backend** - Empowering education through intelligent conversation 🎓✨
