"""
Ingestion Service
Logic for web scraping, PDF parsing, and document chunking.
"""

import asyncio
import aiohttp
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse

import pypdf
from bs4 import BeautifulSoup
from docx import Document
import chardet

from core.config import get_settings
from models.admin_models import IngestionRequest

logger = logging.getLogger(__name__)
settings = get_settings()


class IngestionService:
    """Service for handling document ingestion and processing."""
    
    def __init__(self):
        self.supported_extensions = settings.supported_file_types
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    async def process_ingestion(self, request: IngestionRequest) -> Dict[str, Any]:
        """
        Process an ingestion request and return processed documents.
        
        Args:
            request: The ingestion request containing source type and data
            
        Returns:
            Dictionary containing processed chunks and metadata
        """
        try:
            if request.source_type == "url":
                return await self._process_url(request.source_data, request.metadata)
            elif request.source_type == "file":
                return await self._process_file(request.source_data, request.metadata)
            elif request.source_type == "text":
                return await self._process_text(request.source_data, request.metadata)
            else:
                raise ValueError(f"Unsupported source type: {request.source_type}")
                
        except Exception as e:
            logger.error(f"Error processing ingestion: {str(e)}")
            raise

    async def _process_url(self, url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process content from a URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch URL: HTTP {response.status}")
                    
                    content_type = response.headers.get('content-type', '').lower()
                    content = await response.read()
                    
                    if 'text/html' in content_type:
                        text_content = self._extract_html_content(content.decode('utf-8'))
                    elif 'application/pdf' in content_type:
                        text_content = self._extract_pdf_content(content)
                    else:
                        # Try to decode as text
                        encoding = chardet.detect(content)['encoding'] or 'utf-8'
                        text_content = content.decode(encoding)
                    
                    chunks = self._chunk_text(text_content)
                    
                    return {
                        "source_url": url,
                        "content_type": content_type,
                        "total_chunks": len(chunks),
                        "chunks": chunks,
                        "metadata": {
                            **metadata,
                            "processed_at": datetime.utcnow().isoformat(),
                            "original_length": len(text_content)
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            raise

    async def _process_file(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process content from a local file."""
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_path_obj.stat().st_size > self.max_file_size:
                raise ValueError(f"File too large: {file_path_obj.stat().st_size} bytes")
            
            extension = file_path_obj.suffix.lower()
            
            if extension not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {extension}")
            
            if extension == '.pdf':
                text_content = self._extract_pdf_from_file(file_path)
            elif extension == '.docx':
                text_content = self._extract_docx_content(file_path)
            else:
                # Plain text files
                with open(file_path, 'rb') as f:
                    raw_content = f.read()
                    encoding = chardet.detect(raw_content)['encoding'] or 'utf-8'
                    text_content = raw_content.decode(encoding)
            
            chunks = self._chunk_text(text_content)
            
            return {
                "source_file": str(file_path),
                "file_type": extension,
                "file_size": file_path_obj.stat().st_size,
                "total_chunks": len(chunks),
                "chunks": chunks,
                "metadata": {
                    **metadata,
                    "processed_at": datetime.utcnow().isoformat(),
                    "original_length": len(text_content)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    async def _process_text(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw text content."""
        try:
            chunks = self._chunk_text(text)
            
            return {
                "source_type": "raw_text",
                "total_chunks": len(chunks),
                "chunks": chunks,
                "metadata": {
                    **metadata,
                    "processed_at": datetime.utcnow().isoformat(),
                    "original_length": len(text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            raise

    def _extract_html_content(self, html: str) -> str:
        """Extract text content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    def _extract_pdf_content(self, pdf_bytes: bytes) -> str:
        """Extract text content from PDF bytes."""
        # TODO: Implement PDF extraction from bytes
        # This would typically use PyPDF2 or pdfplumber
        raise NotImplementedError("PDF extraction from bytes not implemented yet")

    def _extract_pdf_from_file(self, file_path: str) -> str:
        """Extract text content from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            raise
        return text

    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text content from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX content: {str(e)}")
            raise

    def _chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks for vector embedding.
        
        Args:
            text: The input text to chunk
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not text.strip():
            return []
        
        chunks = []
        words = text.split()
        
        # Simple word-based chunking
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Generate chunk ID
            chunk_id = hashlib.md5(chunk_text.encode()).hexdigest()
            
            chunks.append({
                "id": chunk_id,
                "content": chunk_text,
                "word_count": len(chunk_words),
                "chunk_index": len(chunks),
                "start_word": i,
                "end_word": min(i + self.chunk_size, len(words))
            })
        
        return chunks

    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash for content deduplication."""
        return hashlib.sha256(content.encode()).hexdigest()

    def validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False