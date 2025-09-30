# Orion Backend - Requirements Guide

This project uses a modular dependency management approach with separate requirements files for different use cases.

## 📁 Requirements Files

### `requirements.txt` - Production Dependencies (Essential)
- **Size**: ~50 core dependencies
- **Purpose**: Minimal production setup
- **Includes**: FastAPI, database, AI, authentication, crawling, basic utilities
- **Install**: `pip install -r requirements.txt`

### `requirements-dev.txt` - Development Dependencies
- **Purpose**: Development, testing, and code quality tools
- **Includes**: pytest, black, mypy, linting tools
- **Install**: `pip install -r requirements-dev.txt`

### `requirements-optional.txt` - Optional Features
- **Purpose**: ML libraries, demos, analytics, cloud services
- **Includes**: PyTorch, Streamlit, Supabase, advanced monitoring
- **Install**: `pip install -r requirements-optional.txt`

## 🚀 Installation Commands

### Basic Production Setup
```bash
pip install -r requirements.txt
```

### Development Setup
```bash
pip install -r requirements-dev.txt
```

### Full Feature Setup (All Dependencies)
```bash
pip install -r requirements-optional.txt
```

### Custom Setup Examples

**Backend API Only:**
```bash
pip install -r requirements.txt
```

**With Development Tools:**
```bash
pip install -r requirements-dev.txt
```

**With Machine Learning:**
```bash
pip install -r requirements.txt
pip install torch transformers scikit-learn
```

**With Streamlit Demos:**
```bash
pip install -r requirements.txt
pip install streamlit altair
```

## 📊 Dependency Breakdown

### Core Production (~50 dependencies)
- FastAPI ecosystem
- Database (PostgreSQL, Redis)
- Authentication & Security
- AI (Gemini, Anthropic, ChromaDB)
- Document processing
- Web crawling (Crawl4AI)

### Development (~15 additional)
- Testing frameworks
- Code formatting
- Type checking
- Development utilities

### Optional (~70 additional)
- Heavy ML libraries (PyTorch, Transformers)
- Cloud services (Supabase, AWS)
- Analytics and monitoring
- Interactive demos (Streamlit)
- Advanced AI providers

## 🎯 Choosing the Right Setup

**For Production Deployment:**
```bash
pip install -r requirements.txt
```

**For Local Development:**
```bash
pip install -r requirements-dev.txt
```

**For ML Experimentation:**
```bash
pip install -r requirements.txt
pip install torch transformers pandas scikit-learn
```

**For Full Demo Environment:**
```bash
pip install -r requirements-optional.txt
```

## 🔧 Managing Dependencies

### Adding New Dependencies

**Production dependency:**
Add to `requirements.txt`

**Development tool:**
Add to `requirements-dev.txt`

**Optional feature:**
Add to `requirements-optional.txt`

### Updating Dependencies
```bash
# Update production
pip install -r requirements.txt --upgrade

# Update development
pip install -r requirements-dev.txt --upgrade

# Update all
pip install -r requirements-optional.txt --upgrade
```

## 💡 Benefits

1. **Faster installs**: Production setup is 70% smaller
2. **Clearer separation**: Dev tools separate from production
3. **Flexible deployment**: Choose what you need
4. **Better maintenance**: Easier to track dependency purposes
5. **Reduced conflicts**: Fewer unnecessary dependencies

## 🚨 Important Notes

- Always start with `requirements.txt` for core functionality
- Dev tools are only needed for development
- Optional features can be installed as needed
- The files use `-r requirements.txt` to include base dependencies