"""
Test script to verify ChromaDB integration with document processing.
"""

import asyncio
import os
import sys

# Add the path to import ChromaDB utilities
sys.path.append(os.path.join(os.path.dirname(__file__), 'workers', 'crawl4AI-agent-v2'))

from services.ingestion_service import IngestionService
from models.admin_models import IngestionRequest

# Import ChromaDB utilities
from utils import (
    get_chroma_client,
    get_or_create_collection,
    query_collection
)

async def test_chromadb_integration():
    """Test ChromaDB integration with document processing."""
    print("Testing ChromaDB integration with document processing...")
    
    # Initialize ingestion service
    ingestion_service = IngestionService()
    
    # Test text file processing and storage
    print("\n1. Processing and storing text file...")
    try:
        # Create ingestion request for text file
        request = IngestionRequest(
            source_type="file",
            source_data="test_document.txt",
            metadata={"test": "chromadb_integration_test", "source": "test_document.txt"}
        )
        
        # Process the document
        result = await ingestion_service.process_ingestion(request)
        
        print(f"   Processed {result['total_chunks']} chunks from {result['source_file']}")
        
        # Import and use RAG service to store in ChromaDB
        from services.rag_service import RAGService
        rag_service = RAGService()
        
        # Prepare documents for indexing
        documents = []
        for chunk in result['chunks']:
            documents.append({
                "id": chunk["id"],
                "content": chunk["content"],
                "metadata": {
                    **result['metadata'],
                    "chunk_index": chunk["chunk_index"],
                    "word_count": chunk["word_count"]
                }
            })
        
        # Add documents to vector index (ChromaDB)
        success = await rag_service.add_documents_to_index(documents)
        
        if success:
            print("   ✓ Documents successfully added to ChromaDB")
        else:
            print("   ✗ Failed to add documents to ChromaDB")
            return False
        
    except Exception as e:
        print(f"   ✗ Document processing and storage failed: {e}")
        return False
    
    # Verify documents are stored in ChromaDB
    print("\n2. Verifying documents in ChromaDB...")
    try:
        # Get ChromaDB client and collection
        chroma_client = get_chroma_client("./workers/crawl4AI-agent-v2/chroma_db")
        collection = get_or_create_collection(chroma_client, "documents")
        
        # Query for our test documents
        query_results = query_collection(
            collection,
            "test document processing functionality",
            n_results=5
        )
        
        if query_results and query_results.get("ids") and len(query_results["ids"][0]) > 0:
            print(f"   ✓ Found {len(query_results['ids'][0])} documents in ChromaDB")
            print(f"   First document ID: {query_results['ids'][0][0]}")
            print(f"   First document content (first 100 chars): {query_results['documents'][0][0][:100]}...")
            
            # Display metadata if available
            if query_results.get("metadatas") and query_results["metadatas"][0]:
                first_metadata = query_results["metadatas"][0][0]
                print(f"   First document metadata: {first_metadata}")
        else:
            print("   ⚠ No documents found in ChromaDB")
            
    except Exception as e:
        print(f"   ✗ Failed to query ChromaDB: {e}")
        return False
    
    print("\n✓ ChromaDB integration test completed successfully!")
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_chromadb_integration())
    if success:
        print("\n🎉 ChromaDB integration is working correctly!")
    else:
        print("\n❌ ChromaDB integration has issues!")