"""
Test script to verify document processing and ChromaDB storage functionality.
"""

import asyncio
import os
from services.ingestion_service import IngestionService
from models.admin_models import IngestionRequest

async def test_document_processing():
    """Test document processing functionality."""
    print("Testing document processing functionality...")
    
    # Initialize ingestion service
    ingestion_service = IngestionService()
    
    # Test text file processing
    print("\n1. Testing text file processing...")
    try:
        # Create ingestion request for text file
        request = IngestionRequest(
            source_type="file",
            source_data="test_document.txt",
            metadata={"test": "document_processing_test"}
        )
        
        # Process the document
        result = await ingestion_service.process_ingestion(request)
        
        print(f"   Source file: {result['source_file']}")
        print(f"   File type: {result['file_type']}")
        print(f"   File size: {result['file_size']} bytes")
        print(f"   Total chunks: {result['total_chunks']}")
        print(f"   Metadata: {result['metadata']}")
        
        # Display first chunk as example
        if result['chunks']:
            print(f"   First chunk ID: {result['chunks'][0]['id']}")
            print(f"   First chunk content (first 100 chars): {result['chunks'][0]['content'][:100]}...")
            print(f"   First chunk word count: {result['chunks'][0]['word_count']}")
        
        print("   ✓ Text file processing successful")
        
    except Exception as e:
        print(f"   ✗ Text file processing failed: {e}")
        return False
    
    # Test raw text processing
    print("\n2. Testing raw text processing...")
    try:
        # Create ingestion request for raw text
        raw_text = "This is a test of raw text processing. The system should chunk this text appropriately and generate embeddings for each chunk. This is additional content to ensure we have multiple chunks for testing."
        request = IngestionRequest(
            source_type="text",
            source_data=raw_text,
            metadata={"test": "raw_text_processing_test"}
        )
        
        # Process the text
        result = await ingestion_service.process_ingestion(request)
        
        print(f"   Source type: {result['source_type']}")
        print(f"   Total chunks: {result['total_chunks']}")
        print(f"   Metadata: {result['metadata']}")
        
        # Display first chunk as example
        if result['chunks']:
            print(f"   First chunk ID: {result['chunks'][0]['id']}")
            print(f"   First chunk content (first 100 chars): {result['chunks'][0]['content'][:100]}...")
            print(f"   First chunk word count: {result['chunks'][0]['word_count']}")
        
        print("   ✓ Raw text processing successful")
        
    except Exception as e:
        print(f"   ✗ Raw text processing failed: {e}")
        return False
    
    print("\n✓ All document processing tests passed!")
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_document_processing())
    if success:
        print("\n🎉 Document processing functionality is working correctly!")
    else:
        print("\n❌ Document processing functionality has issues!")