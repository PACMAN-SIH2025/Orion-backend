"""
RAG Service
Core RAG pipeline logic for embedding, retrieval, and generation.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import google.generativeai as genai

from core.config import get_settings
from models.chat_models import ChatRequest, ChatResponse, SourceDocument

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    """Service for handling RAG pipeline operations."""
    
    def __init__(self):
        self.embedding_model = settings.embedding_model
        self.llm_model = settings.llm_model
        self.max_tokens = settings.max_tokens
        
        # Initialize Gemini AI
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.genai_model = genai.GenerativeModel(self.llm_model)
            self.embedding_service = genai
        else:
            logger.warning("Gemini API key not configured")
            self.genai_model = None
            self.embedding_service = None
        
    async def process_query(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat query through the RAG pipeline.
        
        Args:
            request: The chat request from the user
            
        Returns:
            ChatResponse with generated answer and sources
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Generate embedding for the query
            query_embedding = await self._generate_embedding(request.message)
            
            # Step 2: Retrieve relevant documents
            relevant_docs = await self._retrieve_documents(
                query_embedding, 
                limit=5,
                threshold=0.7
            )
            
            # Step 3: Generate response using LLM
            response_text = await self._generate_response(
                request.message,
                relevant_docs,
                request.max_tokens or self.max_tokens
            )
            
            # Step 4: Format sources
            sources = self._format_sources(relevant_docs) if request.include_sources else None
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ChatResponse(
                response=response_text,
                session_id=request.session_id or self._generate_session_id(),
                message_id=self._generate_message_id(),
                timestamp=datetime.utcnow(),
                sources=sources,
                confidence_score=self._calculate_confidence(relevant_docs),
                processing_time_ms=int(processing_time),
                token_usage=self._get_token_usage()  # TODO: Implement token tracking
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for input text using Gemini.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            if not self.embedding_service:
                logger.warning("Gemini embedding service not configured, using dummy embedding")
                return [0.1] * 768  # Gemini embeddings are typically 768 dimensions
            
            logger.info(f"Generating embedding for text: {text[:100]}...")
            
            # Use Gemini's embedding service
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_query"
                )
            )
            
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Error generating embedding with Gemini: {str(e)}")
            # Fallback to dummy embedding
            return [0.1] * 768

    async def _retrieve_documents(
        self, 
        query_embedding: List[float], 
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from vector database.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of documents to retrieve
            threshold: Minimum similarity threshold
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # TODO: Implement actual vector database query
            # This would typically query Pinecone, Weaviate, ChromaDB, etc.
            
            logger.info(f"Retrieving documents with limit={limit}, threshold={threshold}")
            
            # Simulate database query
            await asyncio.sleep(0.1)
            
            # Return dummy documents (in real implementation, these would be actual retrieved docs)
            dummy_docs = [
                {
                    "id": "doc_1",
                    "content": "This is a sample document about machine learning concepts...",
                    "metadata": {
                        "title": "Introduction to Machine Learning",
                        "source": "textbook_chapter_1.pdf",
                        "page": 15,
                        "url": "https://example.com/ml-textbook"
                    },
                    "similarity_score": 0.85
                },
                {
                    "id": "doc_2", 
                    "content": "Neural networks are computational models inspired by biological neurons...",
                    "metadata": {
                        "title": "Neural Networks Fundamentals",
                        "source": "research_paper.pdf",
                        "page": 3,
                        "url": "https://example.com/nn-paper"
                    },
                    "similarity_score": 0.78
                }
            ]
            
            # Filter by threshold
            filtered_docs = [doc for doc in dummy_docs if doc["similarity_score"] >= threshold]
            
            return filtered_docs[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    async def _generate_response(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        max_tokens: int
    ) -> str:
        """
        Generate response using Gemini with retrieved context.
        
        Args:
            query: User's question
            context_docs: Retrieved relevant documents
            max_tokens: Maximum tokens for response
            
        Returns:
            Generated response text
        """
        try:
            if not self.genai_model:
                logger.warning("Gemini model not configured, returning placeholder response")
                return (
                    "Based on the provided context, I can help answer your question. "
                    "This is a placeholder response. Please configure Gemini API key to enable AI responses."
                )
            
            # Build context from retrieved documents
            context = self._build_context(context_docs)
            
            # Create prompt
            prompt = self._create_prompt(query, context)
            
            logger.info(f"Generating response with Gemini for query: {query[:100]}...")
            
            # Call Gemini API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.genai_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40
                    )
                )
            )
            
            return response.text if response.text else "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {str(e)}")
            return "I encountered an error while processing your request. Please try again later."

    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            title = doc.get("metadata", {}).get("title", f"Document {i}")
            content = doc.get("content", "")[:500]  # Limit content length
            context_parts.append(f"[Source {i}: {title}]\n{content}\n")
        
        return "\n".join(context_parts)

    def _create_prompt(self, query: str, context: str) -> str:
        """Create prompt for LLM with query and context."""
        return f"""You are an educational AI assistant. Answer the student's question based on the provided context.

Context:
{context}

Question: {query}

Instructions:
- Provide a clear, accurate answer based on the context
- If the context doesn't contain enough information, say so
- Be educational and helpful
- Keep the response concise but informative

Answer:"""

    def _format_sources(self, docs: List[Dict[str, Any]]) -> List[SourceDocument]:
        """Format retrieved documents as source documents."""
        sources = []
        for doc in docs:
            metadata = doc.get("metadata", {})
            sources.append(SourceDocument(
                title=metadata.get("title", "Unknown Document"),
                content_snippet=doc.get("content", "")[:200] + "...",
                url=metadata.get("url"),
                document_type=metadata.get("source", "").split(".")[-1] or "unknown",
                relevance_score=doc.get("similarity_score", 0.0),
                metadata=metadata
            ))
        return sources

    def _calculate_confidence(self, docs: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on retrieved documents."""
        if not docs:
            return 0.0
        
        # Simple confidence calculation based on average similarity
        avg_similarity = sum(doc.get("similarity_score", 0.0) for doc in docs) / len(docs)
        return round(avg_similarity, 2)

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return str(uuid.uuid4())

    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        import uuid
        return str(uuid.uuid4())

    def _get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics."""
        # TODO: Implement actual token tracking
        return {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }

    async def add_documents_to_index(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add processed documents to the vector index.
        
        Args:
            documents: List of processed document chunks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Adding {len(documents)} documents to vector index")
            
            # Import ChromaDB utilities
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'workers', 'crawl4AI-agent-v2'))
            from utils import (
                get_chroma_client,
                get_or_create_collection,
                add_documents_to_collection
            )
            
            # Get ChromaDB client and collection
            chroma_client = get_chroma_client("./workers/crawl4AI-agent-v2/chroma_db")
            collection = get_or_create_collection(chroma_client, "documents")
            
            # Prepare documents for ChromaDB
            ids = []
            contents = []
            metadatas = []
            
            for doc in documents:
                # Generate embedding for document content using Gemini
                embedding = await self._generate_embedding(doc["content"])
                
                # Store in ChromaDB with metadata
                ids.append(doc["id"])
                contents.append(doc["content"])
                metadatas.append({
                    **doc.get("metadata", {}),
                    "id": doc["id"],
                    "content": doc["content"],
                    "embedding": embedding
                })
            
            # Add documents to ChromaDB
            if ids and contents and metadatas:
                add_documents_to_collection(collection, ids, contents, metadatas)
                
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to index: {str(e)}")
            return False

    async def search_similar_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar content in the vector database."""
        query_embedding = await self._generate_embedding(query)
        return await self._retrieve_documents(query_embedding, limit=limit, threshold=0.5)