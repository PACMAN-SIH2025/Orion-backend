# ChromaDB Vector Storage Configuration

The Orion backend is now configured to use ChromaDB for vector data storage in the web scraping workflow.

## 🏗️ **ARCHITECTURE OVERVIEW**

```
Web Scraping → ChromaDB Vector Storage → RAG Queries
     ↓              ↓                        ↓
1. Crawl4AI    2. Store in ChromaDB    3. Query vectors
   - URL input    - Embeddings         - Similarity search  
   - Extract text - Metadata           - Retrieve context
   - Chunk docs   - Collections        - Generate answers
```

## ⚙️ **CHROMADB CONFIGURATION**

### Environment Variables (.env)
```env
# ChromaDB Configuration
CHROMA_DB_DIR=./chroma_db
CHROMA_COLLECTION_NAME=docs
CHROMA_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Key Components

1. **📁 Storage Directory**: `./chroma_db` 
   - Local persistent storage
   - Automatically created when needed
   - Contains embeddings and metadata

2. **📚 Collection**: `docs`
   - Default collection for scraped content
   - Configurable per scraping request
   - Isolated document storage

3. **🤖 Embedding Model**: `all-MiniLM-L6-v2`
   - SentenceTransformers model
   - 384-dimensional embeddings
   - Fast and efficient for similarity search

## 🔧 **IMPLEMENTATION DETAILS**

### ChromaDB Utilities (`workers/crawl4AI-agent-v2/utils.py`)
- ✅ `get_chroma_client()` - Initialize persistent client
- ✅ `get_or_create_collection()` - Manage collections
- ✅ `add_documents_to_collection()` - Batch document insertion
- ✅ `query_collection()` - Similarity search
- ✅ `format_results_as_context()` - Format for RAG

### Admin API Integration (`app/api/v1/admin.py`)
- ✅ `/chromadb-status` - Check ChromaDB configuration
- ✅ `/crawl4ai-scrape` - Trigger scraping with ChromaDB storage
- ✅ Environment-based configuration
- ✅ Background task processing

### Scraping Workflow (`insert_docs.py`)
- ✅ Crawl websites using Crawl4AI
- ✅ Smart chunking by markdown headers
- ✅ Generate embeddings automatically
- ✅ Store in ChromaDB with metadata
- ✅ Batch processing for efficiency

## 🚀 **USAGE WORKFLOW**

### 1. Frontend Input
```javascript
// User enters URL in Knowledge Management
const response = await fetch('/api/v1/admin/crawl4ai-scrape', {
  method: 'POST',
  body: JSON.stringify({
    url: 'https://docs.python.org',
    collection_name: 'docs'
  })
});
```

### 2. Backend Processing
```python
# FastAPI background task
python insert_docs.py https://docs.python.org \
  --collection docs \
  --db-dir ./chroma_db \
  --embedding-model all-MiniLM-L6-v2
```

### 3. ChromaDB Storage
```python
# Automatic vector storage
collection.add(
    documents=chunks,
    metadatas=metadata,
    ids=chunk_ids
)
```

### 4. RAG Queries
```python
# Similarity search for context
results = collection.query(
    query_texts=["user question"],
    n_results=5
)
```

## 📊 **VECTOR STORAGE FEATURES**

### Document Processing
- ✅ **Smart Chunking**: Hierarchical by headers (#, ##, ###)
- ✅ **Metadata Extraction**: Headers, word count, source URL
- ✅ **Automatic IDs**: Unique chunk identifiers
- ✅ **Batch Processing**: Efficient bulk operations

### Embedding Generation
- ✅ **SentenceTransformers**: High-quality embeddings
- ✅ **Automatic Processing**: No manual embedding required
- ✅ **Consistent Model**: Same model for indexing and querying
- ✅ **Cosine Similarity**: Optimized distance function

### Vector Operations
- ✅ **Similarity Search**: Find relevant documents
- ✅ **Metadata Filtering**: Query by source, headers, etc.
- ✅ **Scalable Storage**: Handle large document collections
- ✅ **Persistent Storage**: Data survives restarts

## 🔍 **TESTING & VERIFICATION**

### Check ChromaDB Status
```bash
curl http://localhost:8000/api/v1/admin/chromadb-status
```

### Scrape and Store Documents
```bash
# Via API
curl -X POST http://localhost:8000/api/v1/admin/crawl4ai-scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org"}'

# Direct command
python workers/crawl4AI-agent-v2/insert_docs.py https://docs.python.org
```

### Verify Storage
```bash
# Check directory
ls -la chroma_db/

# Check collections (via Python)
python -c "
import chromadb
client = chromadb.PersistentClient('./chroma_db')
print('Collections:', [c.name for c in client.list_collections()])
"
```

## 📈 **PERFORMANCE CHARACTERISTICS**

### Embedding Model (all-MiniLM-L6-v2)
- **Size**: 22MB model
- **Dimensions**: 384
- **Speed**: ~1000 docs/second
- **Quality**: High for general text

### ChromaDB Storage
- **Format**: SQLite + HDF5
- **Indexing**: HNSW algorithm
- **Memory**: Efficient for 100K+ documents
- **Persistence**: Disk-based storage

### Chunking Strategy
- **Max Size**: 1000 characters
- **Overlap**: None (hierarchical splitting)
- **Preservation**: Semantic boundaries via headers
- **Metadata**: Rich context information

## 🔐 **CONFIGURATION OPTIONS**

### Customizable Parameters
```python
# Collection settings
collection_name = "docs"  # or "python-docs", "web-content", etc.
embedding_model = "all-MiniLM-L6-v2"  # or other SentenceTransformers

# Chunking settings  
chunk_size = 1000  # characters
max_depth = 3      # crawling depth
batch_size = 100   # insertion batch size

# Storage settings
db_directory = "./chroma_db"  # local path
distance_function = "cosine"  # similarity metric
```

The ChromaDB vector storage is now fully configured and ready for production use with the web scraping workflow!