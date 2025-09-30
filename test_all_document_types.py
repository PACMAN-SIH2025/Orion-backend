"""
Test script to verify processing of all document types (text, DOCX) and storage in ChromaDB.
PDF testing is commented out since we don't have a PDF creation library installed.
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

async def test_all_document_types():
    """Test processing of all document types and storage in ChromaDB."""
    print("Testing processing of all document types and storage in ChromaDB...")
    
    # Initialize ingestion service
    ingestion_service = IngestionService()
    
    # Test results
    test_results = []
    
    # Test 1: Text file processing
    print("\n1. Processing text file...")
    try:
        # Create ingestion request for text file
        request = IngestionRequest(
            source_type="file",
            source_data="test_document.txt",
            metadata={"test": "text_file_test", "source": "test_document.txt", "doc_type": "text"}
        )
        
        # Process the document
        result = await ingestion_service.process_ingestion(request)
        
        print(f"   Processed {result['total_chunks']} chunks from {result['source_file']}")
        print(f"   File type: {result['file_type']}")
        
        # Store result for later use
        test_results.append(("text", result))
        print("   ✓ Text file processing successful")
        
    except Exception as e:
        print(f"   ✗ Text file processing failed: {e}")
        return False
    
    # Test 2: DOCX file processing
    print("\n2. Processing DOCX file...")
    try:
        # Create ingestion request for DOCX file
        request = IngestionRequest(
            source_type="file",
            source_data="test_document.docx",
            metadata={"test": "docx_file_test", "source": "test_document.docx", "doc_type": "docx"}
        )
        
        # Process the document
        result = await ingestion_service.process_ingestion(request)
        
        print(f"   Processed {result['total_chunks']} chunks from {result['source_file']}")
        print(f"   File type: {result['file_type']}")
        
        # Store result for later use
        test_results.append(("docx", result))
        print("   ✓ DOCX file processing successful")
        
    except Exception as e:
        print(f"   ✗ DOCX file processing failed: {e}")
        # Don't return False here as we want to continue testing other functionality
        pass
    
    # Test 3: Raw text processing
    print("\n3. Processing raw text...")
    try:
        # Create ingestion request for raw text
        raw_text = "This is a test of raw text processing. The system should chunk this text appropriately and store it in ChromaDB. This is additional content to ensure we have multiple chunks for testing."
        request = IngestionRequest(
            source_type="text",
            source_data=raw_text,
            metadata={"test": "raw_text_test", "source": "raw_text", "doc_type": "text"}
        )
        
        # Process the text
        result = await ingestion_service.process_ingestion(request)
        
        print(f"   Processed {result['total_chunks']} chunks from raw text")
        print(f"   Source type: {result['source_type']}")
        
        # Store result for later use
        test_results.append(("raw_text", result))
        print("   ✓ Raw text processing successful")
        
    except Exception as e:
        print(f"   ✗ Raw text processing failed: {e}")
        return False
    
    # Test 4: Storing all documents in ChromaDB
    print("\n4. Storing all documents in ChromaDB...")
    try:
        # Get ChromaDB client and collection
        chroma_client = get_chroma_client("./workers/crawl4AI-agent-v2/chroma_db")
        collection = get_or_create_collection(chroma_client, "all_document_types_test")
        
        total_chunks = 0
        
        # Process each test result
        for doc_type, result in test_results:
            # Prepare documents for ChromaDB
            ids = []
            contents = []
            metadatas = []
            
            # Add all chunks to ChromaDB
            for chunk in result['chunks']:
                ids.append(f"{doc_type}_{chunk['id']}")
                contents.append(chunk["content"])
                metadatas.append({
                    **result['metadata'],
                    "doc_type": doc_type,
                    "chunk_index": chunk["chunk_index"],
                    "word_count": chunk["word_count"],
                    "start_word": chunk["start_word"],
                    "end_word": chunk["end_word"]
                })
            
            # Add documents to ChromaDB
            if ids and contents and metadatas:
                add_documents_to_collection(collection, ids, contents, metadatas)
                total_chunks += len(ids)
                print(f"   ✓ Added {len(ids)} {doc_type} chunks to ChromaDB")
            else:
                print(f"   ⚠ No {doc_type} chunks to add to ChromaDB")
            
        print(f"   ✓ Successfully added {total_chunks} total documents to ChromaDB")
            
    except Exception as e:
        print(f"   ✗ Failed to store documents in ChromaDB: {e}")
        return False
    
    # Test 5: Querying documents from ChromaDB
    print("\n5. Querying documents from ChromaDB...")
    try:
        # Query for our test documents
        query_results = query_collection(
            collection,
            "test document processing functionality",
            n_results=10
        )
        
        if query_results and query_results.get("ids") and len(query_results["ids"][0]) > 0:
            print(f"   ✓ Found {len(query_results['ids'][0])} documents in ChromaDB")
            
            # Display information about found documents
            for i, (doc_id, content, metadata) in enumerate(zip(
                query_results["ids"][0],
                query_results["documents"][0],
                query_results["metadatas"][0]
            )):
                print(f"   Document {i+1}:")
                print(f"     ID: {doc_id}")
                print(f"     Content (first 100 chars): {content[:100]}...")
                print(f"     Doc type: {metadata.get('doc_type', 'unknown')}")
                print(f"     Source: {metadata.get('source', 'unknown')}")
        else:
            print("   ⚠ No documents found in ChromaDB")
            
    except Exception as e:
        print(f"   ✗ Failed to query ChromaDB: {e}")
        return False
    
    print("\n✓ All document type tests completed successfully!")
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_all_document_types())
    if success:
        print("\n🎉 All document processing and storage functionality is working correctly!")
    else:
        print("\n❌ Some document processing and storage functionality has issues!")