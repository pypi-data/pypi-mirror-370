# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Native Qdrant adapter implementation for Thoth."""

import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ..core.base import (
    BaseThothDocument,
    ColumnNameDocument,
    EvidenceDocument,
    SqlDocument,
    ThothType,
    VectorStoreInterface,
)
from ..core.embedding_manager import ExternalEmbeddingManager

logger = logging.getLogger(__name__)


class QdrantNativeAdapter(VectorStoreInterface):
    """Native Qdrant implementation for Thoth Vector Database."""
    
    _instances: Dict[str, "QdrantNativeAdapter"] = {}
    
    def __new__(
        cls,
        collection: str,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs
    ):
        """Singleton pattern for Qdrant adapter."""
        instance_key = f"{collection}:{host}:{port}:{api_key}"
        if instance_key in cls._instances:
            return cls._instances[instance_key]
        
        instance = super().__new__(cls)
        cls._instances[instance_key] = instance
        return instance
    
    def __init__(
        self,
        collection: str,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        embedding_provider: Optional[str] = None,
        embedding_model: Optional[str] = None,
        embedding_dim: int = 1536,
        **kwargs
    ):
        """Initialize Qdrant native adapter.
        
        Args:
            collection: Collection name
            host: Qdrant host
            port: Qdrant port
            api_key: API key for authentication
            url: Full URL (overrides host/port)
            embedding_provider: External provider (openai, cohere, mistral)
            embedding_model: Model name for the provider
            embedding_dim: Embedding dimension
            **kwargs: Additional Qdrant parameters
        """
        # Prevent reinitialization
        if hasattr(self, '_initialized'):
            return
        
        # Parse URL if provided
        if url:
            parsed = urlparse(url)
            host = parsed.hostname or host
            port = parsed.port or port
        
        # Store configuration
        self.collection_name = collection
        self.host = host
        self.port = port
        self.api_key = api_key
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim
        
        # Initialize Qdrant client
        self.client = QdrantClient(host=host, port=port, api_key=api_key)
        
        # Initialize external embedding manager
        try:
            self.embedding_manager = self._create_external_embedding_manager()
            # Update embedding dimension from provider
            self.embedding_dim = self.embedding_manager.provider.get_dimensions()
        except Exception as e:
            logger.error(f"Failed to initialize external embedding manager: {e}")
            raise
        
        # Ensure collection exists
        self.ensure_collection_exists()
        
        self._initialized = True
        logger.info(f"Qdrant native adapter initialized for collection: {collection}")
    
    def _create_external_embedding_manager(self) -> ExternalEmbeddingManager:
        """Create external embedding manager from environment or parameters."""
        # Priority order: instance parameters -> environment variables
        embedding_provider = self.embedding_provider or os.environ.get('EMBEDDING_PROVIDER')
        embedding_model = self.embedding_model or os.environ.get('EMBEDDING_MODEL')
        
        # Check provider-specific API key environment variables first
        embedding_api_key = None
        if embedding_provider:
            env_key_mappings = {
                'openai': ['OPENAI_API_KEY', 'OPENAI_KEY'],
                'cohere': ['COHERE_API_KEY', 'COHERE_KEY'],
                'mistral': ['MISTRAL_API_KEY', 'MISTRAL_KEY'],
                'huggingface': ['HUGGINGFACE_API_KEY', 'HF_API_KEY', 'HUGGINGFACE_TOKEN'],
            }
            
            provider_keys = env_key_mappings.get(embedding_provider, [])
            for env_key in provider_keys:
                embedding_api_key = os.environ.get(env_key)
                if embedding_api_key:
                    logger.info(f"Found API key in environment variable: {env_key}")
                    break
            
            # Fall back to generic API key
            if not embedding_api_key:
                embedding_api_key = os.environ.get('EMBEDDING_API_KEY')
                if embedding_api_key:
                    logger.info("Found API key in EMBEDDING_API_KEY")
        
        if not embedding_provider or not embedding_api_key:
            raise ValueError(
                f"External embedding provider configuration missing. "
                f"Provider: {embedding_provider}, API Key: {'set' if embedding_api_key else 'missing'}. "
                f"Please configure embedding settings or set environment variables."
            )
        
        logger.info(f"Creating external embedding manager: {embedding_provider} with model {embedding_model}")
        
        # Create manager from configuration
        config = {
            'provider': embedding_provider,
            'api_key': embedding_api_key,
            'model': embedding_model,
            'enable_cache': True,
            'cache_size': 10000
        }
        
        return ExternalEmbeddingManager.from_config(config)
    
    def ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create it if it doesn't."""
        logger.info(f"Ensuring collection exists: {self.collection_name}")
        
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return
            
            # Create collection with proper configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            
            # Create payload index for efficient filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="thoth_type",
                field_schema="keyword"
            )
            
            logger.info(f"Successfully created collection '{self.collection_name}' with {self.embedding_dim}-dimensional vectors")
            
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string input by removing leading/trailing whitespace and newlines."""
        if not value:
            return ""
        # Remove leading/trailing whitespace and replace internal newlines with spaces
        return " ".join(value.strip().split())
    
    def _enrich_content(self, doc: BaseThothDocument) -> str:
        """Enrich document content for embedding."""
        if isinstance(doc, ColumnNameDocument):
            # Sanitize all fields before concatenation
            table_name = self._sanitize_string(doc.table_name)
            column_name = self._sanitize_string(doc.column_name)
            original_column_name = self._sanitize_string(doc.original_column_name)
            column_description = self._sanitize_string(doc.column_description)
            value_description = self._sanitize_string(doc.value_description)
            
            return (
                f"Table: {table_name}, Column: {column_name} "
                f"(Original: {original_column_name}). "
                f"Description: {column_description}. "
                f"Value Info: {value_description}"
            )
        elif isinstance(doc, SqlDocument):
            question = self._sanitize_string(doc.question).lower()
            evidence = self._sanitize_string(doc.evidence).lower()
            return f"{question} {evidence}"
        elif isinstance(doc, EvidenceDocument):
            return self._sanitize_string(doc.evidence)
        else:
            return self._sanitize_string(doc.text)
    
    def _document_to_payload(self, doc: BaseThothDocument) -> Dict[str, Any]:
        """Convert Thoth document to Qdrant payload."""
        if not doc.text:
            doc.text = self._enrich_content(doc)
        
        # Handle enum properly - get value if it's an enum, otherwise use as is
        thoth_type_value = doc.thoth_type.value if hasattr(doc.thoth_type, 'value') else str(doc.thoth_type)
        
        payload = {
            "thoth_type": thoth_type_value,
            "thoth_id": doc.id,
            "text": doc.text,
        }
        
        if isinstance(doc, ColumnNameDocument):
            payload.update({
                "table_name": doc.table_name,
                "column_name": doc.column_name,
                "original_column_name": doc.original_column_name,
                "column_description": doc.column_description,
                "value_description": doc.value_description,
            })
        elif isinstance(doc, SqlDocument):
            payload.update({
                "question": doc.question,
                "sql": doc.sql,
                "evidence": doc.evidence,
            })
        elif isinstance(doc, EvidenceDocument):
            payload.update({
                "evidence": doc.evidence,
            })
        
        return payload
    
    def _payload_to_document(self, payload: Dict[str, Any]) -> Optional[BaseThothDocument]:
        """Convert Qdrant payload to Thoth document."""
        if not payload or "thoth_type" not in payload:
            return None
        
        thoth_type_str = payload["thoth_type"]
        try:
            thoth_type = ThothType(thoth_type_str)
        except ValueError:
            logger.warning(f"Invalid ThothType: {thoth_type_str}")
            return None
        
        doc_id = payload.get("thoth_id", "")
        doc_text = payload.get("text", "")
        
        try:
            if thoth_type == ThothType.COLUMN_NAME:
                return ColumnNameDocument(
                    id=doc_id,
                    text=doc_text,
                    table_name=self._sanitize_string(payload.get("table_name", "")),
                    column_name=self._sanitize_string(payload.get("column_name", "")),
                    original_column_name=self._sanitize_string(payload.get("original_column_name", "")),
                    column_description=self._sanitize_string(payload.get("column_description", "")),
                    value_description=self._sanitize_string(payload.get("value_description", "")),
                )
            elif thoth_type == ThothType.SQL:
                return SqlDocument(
                    id=doc_id,
                    text=doc_text,
                    question=self._sanitize_string(payload.get("question", "")),
                    sql=self._sanitize_string(payload.get("sql", "")),
                    evidence=self._sanitize_string(payload.get("evidence", "")),
                )
            elif thoth_type == ThothType.EVIDENCE:
                return EvidenceDocument(
                    id=doc_id,
                    text=doc_text,
                    evidence=self._sanitize_string(payload.get("evidence", doc_text)),
                )
        except Exception as e:
            logger.error(f"Error converting payload to document. Payload keys: {list(payload.keys())}, Error: {e}")
            # Log problematic field values for debugging
            if 'column_name' in payload:
                logger.debug(f"Problematic column_name value: {repr(payload['column_name'])}")
            if 'table_name' in payload:
                logger.debug(f"Problematic table_name value: {repr(payload['table_name'])}")
            return None
    
    def _add_document_with_embedding(self, doc: BaseThothDocument) -> str:
        """Add document with embedding to Qdrant."""
        # Ensure text is enriched
        if not doc.text:
            doc.text = self._enrich_content(doc)
        
        # Generate embedding
        embedding = self.embedding_manager.encode_query(doc.text)
        
        # Create Qdrant point
        point = PointStruct(
            id=doc.id,
            vector=embedding,
            payload=self._document_to_payload(doc)
        )
        
        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        logger.debug(f"Added document {doc.id} of type {doc.thoth_type}")
        return doc.id
    
    def add_column_description(self, doc: ColumnNameDocument) -> str:
        """Add a column description document."""
        return self._add_document_with_embedding(doc)
    
    def add_sql(self, doc: SqlDocument) -> str:
        """Add an SQL document."""
        return self._add_document_with_embedding(doc)
    
    def add_evidence(self, doc: EvidenceDocument) -> str:
        """Add an evidence document."""
        return self._add_document_with_embedding(doc)
    
    def search_similar(
        self,
        query: str,
        doc_type: ThothType,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[BaseThothDocument]:
        """Search for similar documents using Qdrant."""
        if not query:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_manager.encode_query(query)
            
            # Create filter for document type
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="thoth_type",
                        match=MatchValue(value=doc_type.value)
                    )
                ]
            )
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=score_threshold
            )
            
            # Convert results to Thoth documents
            documents = []
            for result in search_results:
                doc = self._payload_to_document(result.payload)
                if doc:
                    documents.append(doc)
            
            logger.debug(f"Found {len(documents)} similar documents of type {doc_type}")
            return documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_document(self, doc_id: str) -> Optional[BaseThothDocument]:
        """Get a document by ID."""
        try:
            # Retrieve point from Qdrant
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[doc_id]
            )
            
            if points:
                return self._payload_to_document(points[0].payload)
            
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
        
        return None
    
    def delete_document(self, doc_id: str) -> None:
        """Delete a document by ID."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[doc_id]
            )
            logger.debug(f"Deleted document {doc_id}")
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "backend": "qdrant",
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_config": {
                    "size": collection_info.config.params.vectors.size,
                    "distance": str(collection_info.config.params.vectors.distance),
                },
                "embedding_provider": self.embedding_provider,
                "embedding_model": self.embedding_model,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "backend": "qdrant",
                "collection_name": self.collection_name,
                "error": str(e)
            }
    
    def bulk_add_documents(self, documents: List[BaseThothDocument], policy: Optional[str] = None) -> List[str]:
        """Add multiple documents in batch."""
        if not documents:
            return []
        
        # Enrich text content for all documents
        for doc in documents:
            if not doc.text:
                doc.text = self._enrich_content(doc)
        
        # Generate embeddings in batch
        texts = [doc.text for doc in documents]
        embeddings = self.embedding_manager.encode_texts(texts)
        
        # Create Qdrant points
        points = []
        for doc, embedding in zip(documents, embeddings):
            point = PointStruct(
                id=doc.id,
                vector=embedding,
                payload=self._document_to_payload(doc)
            )
            points.append(point)
        
        # Batch upsert to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        doc_ids = [doc.id for doc in documents]
        logger.info(f"Bulk added {len(documents)} documents")
        return doc_ids
    
    def delete_collection(self, thoth_type: ThothType) -> None:
        """Delete all documents of a specific type."""
        try:
            # Delete points with matching thoth_type
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="thoth_type",
                            match=MatchValue(value=thoth_type.value)
                        )
                    ]
                )
            )
            logger.info(f"Deleted all documents of type {thoth_type}")
        except Exception as e:
            logger.error(f"Error deleting documents of type {thoth_type}: {e}")
    
    def _get_all_documents(self) -> List[BaseThothDocument]:
        """Get all documents from the collection."""
        documents = []
        offset = None
        
        try:
            while True:
                # Scroll through all points
                records, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=100,
                    offset=offset
                )
                
                for record in records:
                    doc = self._payload_to_document(record.payload)
                    if doc:
                        documents.append(doc)
                
                if next_offset is None:
                    break
                offset = next_offset
                
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
        
        return documents
    
    def get_documents_by_type(self, thoth_type: ThothType) -> List[BaseThothDocument]:
        """Get all documents of a specific type.
        
        Args:
            thoth_type: The type of documents to retrieve
            
        Returns:
            List of documents of the specified type
        """
        documents = []
        offset = None
        
        try:
            # Create filter for the specific type
            must_conditions = [
                models.FieldCondition(
                    key="thoth_type",
                    match=models.MatchValue(value=thoth_type.value)
                )
            ]
            
            while True:
                # Scroll through points with type filter
                records, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=models.Filter(must=must_conditions),
                    limit=100,
                    offset=offset
                )
                
                for record in records:
                    doc = self._payload_to_document(record.payload)
                    if doc:
                        documents.append(doc)
                
                if next_offset is None:
                    break
                offset = next_offset
                
        except Exception as e:
            logger.error(f"Error getting documents by type {thoth_type}: {e}")
        
        return documents
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "QdrantNativeAdapter":
        """Create Qdrant adapter from configuration."""
        return cls(**config)