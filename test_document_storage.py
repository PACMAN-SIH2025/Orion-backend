"""
Test script to verify document processing and storage in ChromaDB.
This test focuses on the document processing pipeline and ChromaDB storage
without requiring external APIs like Gemini.
"""

import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'workers', 'crawl4AI-agent-v2'))

from services.ingestion_service import IngestionService
from models.admin_models import IngestionRequest
from utils import (
    get_chroma_client,
    get_or_create_collection,
    add_documents_to_collection,
    query_collection
)

async def test_document_storage():
    """Test document processing and storage in ChromaDB."""
    print("Testing document processing and storage in ChromaDB...")
    
    # Initialize ingestion service
    ingestion_service = IngestionService()
    
    # Test text file processing
    print("\n1. Processing text file...")
    try:
        # Create ingestion request for text file
        request = IngestionRequest(
            source_type="file",
            source_data="test_document.txt",
            metadata={"test": "document_storage_test", "source": "test_document.txt"}
        )
        
        # Process the document
        result = await ingestion_service.process_ingestion(request)
        
        print(f"   Processed {result['total_chunks']} chunks from {result['source_file']}")
        print(f"   File type: {result['file_type']}")
        print(f"   File size: {result['file_size']} bytes")
        
        # Display first chunk as example
        if result['chunks']:
            print(f"   First chunk ID: {result['chunks'][0]['id']}")
            print(f"   First chunk content (first 100 chars): {result['chunks'][0]['content'][:100]}...")
            print(f"   First chunk word count: {result['chunks'][0]['word_count']}")
        
        print("   ✓ Text file processing successful")
        
    except Exception as e:
        print(f"   ✗ Text file processing failed: {e}")
        return False
    
    # Test storing documents in ChromaDB
    print("\n2. Storing documents in ChromaDB...")
    try:
        # Get ChromaDB client and collection
        chroma_client = get_chroma_client("./workers/crawl4AI-agent-v2/chroma_db")
        collection = get_or_create_collection(chroma_client, "test_documents")
        
        # Prepare documents for ChromaDB
        ids = []
        contents = []
        metadatas = []
        
        # Add all chunks to ChromaDB
        for chunk in result['chunks']:
            ids.append(chunk["id"])
            contents.append(chunk["content"])
            metadatas.append({
                **result['metadata'],
                "chunk_index": chunk["chunk_index"],
                "word_count": chunk["word_count"],
                "start_word": chunk["start_word"],
                "end_word": chunk["end_word"]
            })
        
        # Add documents to ChromaDB
        if ids and contents and metadatas:
            add_documents_to_collection(collection, ids, contents, metadatas)
            print(f"   ✓ Successfully added {len(ids)} documents to ChromaDB")
        else:
            print("   ⚠ No documents to add to ChromaDB")
            return False
            
    except Exception as e:
        print(f"   ✗ Failed to store documents in ChromaDB: {e}")
        return False
    
    # Test querying documents from ChromaDB
    print("\n3. Querying documents from ChromaDB...")
    try:
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
    
    print("\n✓ Document storage test completed successfully!")
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_document_storage())
    if success:
        print("\n🎉 Document processing and storage functionality is working correctly!")
    else:
        print("\n❌ Document processing and storage functionality has issues!")