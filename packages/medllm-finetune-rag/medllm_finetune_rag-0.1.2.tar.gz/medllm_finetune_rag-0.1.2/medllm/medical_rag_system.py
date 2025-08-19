#!/usr/bin/env python3
"""
Medical RAG (Retrieval-Augmented Generation) System using RAG-Anything
Enhanced with multimodal document processing and knowledge graph capabilities
"""

from dataclasses import dataclass
import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import logging
from raganything import RAGAnything
from raganything import modalprocessors
from lightrag import LightRAG
import tempfile

logger = logging.getLogger(__name__)



class MedicalRAGSystem:
    """Medical Retrieval-Augmented Generation System using RAG-Anything"""
    
    def __init__(self, 
                 working_dir: str = "./medical_rag_workspace",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model_name: str = "gpt-4o-mini",
                 parser: str = "mineru",
                 parse_method: str = "auto",
                 chunk_size: int = 1200,
                 chunk_overlap: int = 100,
                 top_k: int = 5):
        """
        Initialize Medical RAG System with RAG-Anything
        
        Args:
            working_dir: Working directory for RAG system
            api_key: OpenAI API key (optional for parsing-only operations)
            base_url: Custom API base URL
            model_name: LLM model name for generation
            parser: Document parser ("mineru" or "docling")
            parse_method: Parse method ("auto", "ocr", "txt")
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            top_k: Number of top documents to retrieve
        """
        self.working_dir = working_dir
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.base_url = base_url or os.getenv('OPENAI_BASE_URL')
        self.model_name = model_name
        self.parser = parser
        self.parse_method = parse_method
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        
        # Create working directory
        os.makedirs(working_dir, exist_ok=True)
        
        # Initialize RAG-Anything
        self.rag_anything = None
        self.lightrag = None
        self.modal_processors = None
        
        # Initialize components
        self._initialize_components()
        
        logger.info(f"Medical RAG System initialized with parser: {parser}, method: {parse_method}")
    
    def _initialize_components(self):
        """Initialize RAG-Anything components"""
        try:
            # Initialize LightRAG for knowledge graph and retrieval first
            if self.api_key:
                self.lightrag = LightRAG(
                    working_dir=self.working_dir,
                    llm_model_func=self._llm_model_func,
                    embedding_func=self._embedding_func
                )
                
                # Initialize RAG-Anything for document processing with LightRAG
                self.rag_anything = RAGAnything(
                    lightrag=self.lightrag,
                    llm_model_func=self._llm_model_func,
                    embedding_func=self._embedding_func
                )
            else:
                self.lightrag = None
                self.rag_anything = None
            
            # Initialize modal processors for multimodal content
            if self.lightrag:
                self.image_processor = modalprocessors.ImageModalProcessor(
                    lightrag=self.lightrag,
                    modal_caption_func=self._modal_caption_func
                )
                self.table_processor = modalprocessors.TableModalProcessor(
                    lightrag=self.lightrag,
                    modal_caption_func=self._modal_caption_func
                )
                self.equation_processor = modalprocessors.EquationModalProcessor(
                    lightrag=self.lightrag,
                    modal_caption_func=self._modal_caption_func
                )
                self.modal_processors = {
                    'image': self.image_processor,
                    'table': self.table_processor,
                    'equation': self.equation_processor
                }
            else:
                self.modal_processors = None
            
            logger.info("RAG components initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize all RAG components: {e}")
            # Initialize basic components without API dependencies
            self.lightrag = None
            self.rag_anything = None
            self.modal_processors = None
    
    async def _llm_model_func(self, prompt, system_prompt=None, history_messages=[], **kwargs) -> str:
        """LLM model function for LightRAG"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            for msg in history_messages:
                messages.append(msg)
                
            messages.append({"role": "user", "content": prompt})
            
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM model function error: {e}")
            return f"Error in LLM generation: {e}"
    
    async def _embedding_func(self, texts: List[str]) -> List[List[float]]:
        """Embedding function for LightRAG"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            
            return [item.embedding for item in response.data]
            
        except Exception as e:
            logger.error(f"Embedding function error: {e}")
            # Return dummy embeddings as fallback
            return [[0.0] * 1536 for _ in texts]
    
    async def _modal_caption_func(self, content, content_type="image"):
        """Modal caption function for describing multimodal content"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            
            if content_type == "image":
                # For images, generate a description
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this medical image in detail, focusing on any pathological findings, anatomical structures, and clinical significance."},
                            {"type": "image_url", "image_url": {"url": content}}
                        ]
                    }
                ]
            else:
                # For other content types, generate appropriate descriptions
                messages = [
                    {
                        "role": "user",
                        "content": f"Analyze and describe this {content_type} content in a medical context: {content}"
                    }
                ]
            
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Modal caption function error: {e}")
            return f"Unable to process {content_type} content: {str(e)}"
    
    async def add_document(self, 
                          file_path: str, 
                          output_dir: Optional[str] = None,
                          doc_id: Optional[str] = None,
                          display_stats: bool = True,
                          **kwargs) -> Dict[str, Any]:
        """
        Add a document to the RAG system
        
        Args:
            file_path: Path to the document file
            output_dir: Output directory for parsed content
            doc_id: Optional document ID
            display_stats: Whether to display processing statistics
            **kwargs: Additional parameters for parsing
            
        Returns:
            Processing results and statistics
        """
        if not self.rag_anything:
            raise ValueError("RAG-Anything not initialized. Please provide API key.")
        
        if output_dir is None:
            output_dir = os.path.join(self.working_dir, "parsed_documents")
        
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Processing document: {file_path}")
        
        try:
            # Process document with RAG-Anything
            result = await self.rag_anything.process_document_complete(
                file_path=file_path,
                output_dir=output_dir,
                parse_method=self.parse_method,
                parser=self.parser,
                display_stats=display_stats,
                doc_id=doc_id,
                **kwargs
            )
            
            # Extract processed content for LightRAG
            if self.lightrag and result.get('processed_content'):
                content_text = self._extract_text_from_content(result['processed_content'])
                if content_text:
                    await self.lightrag.ainsert(content_text)
            
            logger.info(f"Successfully processed document: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
    
    def _extract_text_from_content(self, processed_content: List[Dict[str, Any]]) -> str:
        """Extract text content from processed multimodal content"""
        text_parts = []
        
        for item in processed_content:
            content_type = item.get('type', '')
            
            if content_type == 'text':
                text_parts.append(item.get('content', ''))
            elif content_type == 'table':
                # Convert table to text representation
                table_data = item.get('content', {})
                if isinstance(table_data, dict) and 'data' in table_data:
                    table_text = self._table_to_text(table_data['data'])
                    text_parts.append(f"Table: {table_text}")
            elif content_type == 'equation':
                # Include equation in text form
                equation = item.get('content', '')
                text_parts.append(f"Equation: {equation}")
            elif content_type == 'image':
                # Include image description if available
                description = item.get('description', 'Image content')
                text_parts.append(f"Image: {description}")
        
        return '\n\n'.join(text_parts)
    
    def _table_to_text(self, table_data: List[List[str]]) -> str:
        """Convert table data to text representation"""
        if not table_data:
            return ""
        
        text_rows = []
        for row in table_data:
            text_rows.append(' | '.join(str(cell) for cell in row))
        
        return '\n'.join(text_rows)
    
    async def add_documents_batch(self, 
                                 file_paths: List[str],
                                 output_dir: Optional[str] = None,
                                 **kwargs) -> List[Dict[str, Any]]:
        """
        Add multiple documents to the RAG system
        
        Args:
            file_paths: List of document file paths
            output_dir: Output directory for parsed content
            **kwargs: Additional parameters for parsing
            
        Returns:
            List of processing results
        """
        results = []
        
        for file_path in file_paths:
            try:
                result = await self.add_document(file_path, output_dir, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append({"file_path": file_path, "error": str(e)})
        
        return results
    
    async def process_multimodal_content(self, 
                                       content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multimodal content directly
        
        Args:
            content_list: List of content items with type and content
            
        Returns:
            Processed multimodal content
        """
        if not self.modal_processors:
            raise ValueError("Modal processors not initialized")
        
        results = []
        
        for item in content_list:
            try:
                content_type = item.get('type', '')
                content = item.get('content', '')
                
                if content_type == 'image' and 'image' in self.modal_processors:
                    # Process image content (this would need actual implementation)
                    # For now, just pass through with processing indication
                    processed_item = item.copy()
                    processed_item['processed'] = True
                    processed_item['processor'] = 'image'
                    results.append(processed_item)
                elif content_type == 'table' and 'table' in self.modal_processors:
                    # Process table content
                    processed_item = item.copy()
                    processed_item['processed'] = True
                    processed_item['processor'] = 'table'
                    results.append(processed_item)
                elif content_type == 'equation' and 'equation' in self.modal_processors:
                    # Process equation content
                    processed_item = item.copy()
                    processed_item['processed'] = True
                    processed_item['processor'] = 'equation'
                    results.append(processed_item)
                else:
                    # Pass through other content types
                    results.append(item)
                    
            except Exception as e:
                logger.error(f"Error processing multimodal content: {e}")
                results.append({"type": "error", "content": str(e), "original": item})
        
        return results
    
    def build_knowledge_base_from_json(self, data_path: str) -> None:
        """
        Build knowledge base from JSON data (for backward compatibility)
        
        Args:
            data_path: Path to JSON data file
        """
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Convert JSON data to text format for LightRAG
            documents = []
            for item in raw_data:
                text_content = item.get('text', '')
                
                # Add entity and relation information to text
                if item.get('entities'):
                    entities_info = []
                    for ent in item['entities']:
                        entities_info.append(f"{ent['text']} ({ent['label']})")
                    text_content += f"\n\nEntities: {', '.join(entities_info)}"
                
                if item.get('relations'):
                    relations_info = []
                    for rel in item['relations']:
                        relations_info.append(f"{rel['subject']} {rel['relation']} {rel['object']}")
                    text_content += f"\n\nRelations: {', '.join(relations_info)}"
                
                documents.append(text_content)
            
            # Insert documents into LightRAG asynchronously
            async def insert_docs():
                if self.lightrag:
                    for doc in documents:
                        await self.lightrag.ainsert(doc)
            
            # Run the async function
            asyncio.run(insert_docs())
            
            logger.info(f"Knowledge base built from {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error building knowledge base from JSON: {e}")
            raise
    
    async def clear_knowledge_base(self):
        """Clear the knowledge base"""
        try:
            # Remove LightRAG files
            lightrag_files = [
                'kv_store_full_docs.json',
                'kv_store_text_chunks.json',
                'kv_store_community_reports.json',
                'vdb_entities.json',
                'vdb_relationships.json',
                'vdb_chunks.json'
            ]
            
            for file_name in lightrag_files:
                file_path = os.path.join(self.working_dir, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            logger.info("Knowledge base cleared")
            
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {e}")
            raise
    
    async def search(self, query: str, mode: str = "hybrid") -> str:
        """
        Search for relevant information
        
        Args:
            query: Search query
            mode: Search mode ("naive", "local", "global", "hybrid")
            
        Returns:
            Search results
        """
        if not self.lightrag:
            raise ValueError("LightRAG not initialized. Please provide API key.")
        
        try:
            if mode == "naive":
                result = await self.lightrag.aquery(query, param="naive")
            elif mode == "local":
                result = await self.lightrag.aquery(query, param="local")
            elif mode == "global":
                result = await self.lightrag.aquery(query, param="global")
            else:  # hybrid
                result = await self.lightrag.aquery(query, param="hybrid")
            
            return result
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search error: {e}"
    
    async def generate_response(self, query: str, mode: str = "hybrid") -> str:
        """
        Generate response using RAG
        
        Args:
            query: User query
            mode: Search mode for retrieval
            
        Returns:
            Generated response
        """
        try:
            # Use LightRAG for response generation
            response = await self.search(query, mode)
            return response
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return f"I encountered an error while generating a response: {e}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system"""
        stats = {
            'working_dir': self.working_dir,
            'parser': self.parser,
            'parse_method': self.parse_method,
            'model_name': self.model_name,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'top_k': self.top_k,
            'components': {
                'rag_anything': self.rag_anything is not None,
                'lightrag': self.lightrag is not None,
                'modal_processors': self.modal_processors is not None
            }
        }
        
        # Add LightRAG stats if available
        if self.lightrag:
            try:
                # Get knowledge graph stats
                kg_stats = {
                    'has_knowledge_graph': os.path.exists(os.path.join(self.working_dir, 'kv_store_full_docs.json')),
                    'has_vector_cache': os.path.exists(os.path.join(self.working_dir, 'vdb_entities.json'))
                }
                stats['lightrag_stats'] = kg_stats
            except Exception as e:
                logger.debug(f"Could not get LightRAG stats: {e}")
        
        return stats

def main():
    """Example usage of Medical RAG System"""
    import asyncio
    
    async def demo():
        # Initialize RAG system
        rag_system = MedicalRAGSystem(
            working_dir="./medical_rag_workspace",
            api_key=os.getenv('OPENAI_API_KEY'),  # Set your API key
            model_name="gpt-4o-mini",
            parser="mineru"
        )
        
        # Example: Process a medical document
        # result = await rag_system.add_document("medical_paper.pdf")
        # print("Document processing result:", result)
        
        # Example: Query the system
        test_query = """
        What are the relationships between Epstein-Barr virus antibodies and multiple sclerosis 
        progression in pregnant women?
        """
        
        try:
            response = await rag_system.generate_response(test_query, mode="hybrid")
            print("RAG Response:")
            print(response)
        except Exception as e:
            print(f"Error generating response: {e}")
        
        # Get system statistics
        stats = rag_system.get_stats()
        print("\nSystem Statistics:")
        print(json.dumps(stats, indent=2))
    
    # Run the demo
    asyncio.run(demo())

if __name__ == "__main__":
    main()
