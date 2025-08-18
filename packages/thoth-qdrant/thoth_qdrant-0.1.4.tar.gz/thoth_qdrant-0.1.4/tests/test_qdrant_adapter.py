# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Tests for Qdrant native adapter."""

import os
import pytest
from typing import Dict, Any, List

from thoth_qdrant import VectorStoreFactory
from thoth_qdrant.core.base import (
    ColumnNameDocument,
    SqlDocument,
    EvidenceDocument,
    ThothType,
)


class TestQdrantAdapter:
    """Test Qdrant native adapter implementation."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_config):
        """Set up test environment."""
        # Clean up collection before each test
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(host="localhost", port=6333)
            client.delete_collection(test_config["params"]["collection"])
        except Exception:
            pass  # Collection might not exist
    
    def test_store_creation(self, test_config):
        """Test that the Qdrant vector store can be created successfully."""
        store = VectorStoreFactory.from_config(test_config)
        assert store is not None
        
        # Check collection info
        info = store.get_collection_info()
        assert info["backend"] == "qdrant"
        assert info["collection_name"] == test_config["params"]["collection"]
    
    def test_add_column_description(self, test_config, sample_column_documents):
        """Test adding column description documents."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Add documents
        doc_ids = []
        for doc in sample_column_documents:
            doc_id = store.add_column_description(doc)
            assert doc_id == doc.id
            doc_ids.append(doc_id)
        
        # Verify documents were added
        for doc_id, original_doc in zip(doc_ids, sample_column_documents):
            retrieved_doc = store.get_columns_document_by_id(doc_id)
            assert retrieved_doc is not None
            assert retrieved_doc.table_name == original_doc.table_name
            assert retrieved_doc.column_name == original_doc.column_name
    
    def test_add_sql_document(self, test_config, sample_sql_documents):
        """Test adding SQL documents."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Add documents
        doc_ids = []
        for doc in sample_sql_documents:
            doc_id = store.add_sql(doc)
            assert doc_id == doc.id
            doc_ids.append(doc_id)
        
        # Verify documents were added
        for doc_id, original_doc in zip(doc_ids, sample_sql_documents):
            retrieved_doc = store.get_sql_document_by_id(doc_id)
            assert retrieved_doc is not None
            assert retrieved_doc.question == original_doc.question
            assert retrieved_doc.sql == original_doc.sql
    
    def test_add_evidence_document(self, test_config, sample_evidence_documents):
        """Test adding evidence documents."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Add documents
        doc_ids = []
        for doc in sample_evidence_documents:
            doc_id = store.add_evidence(doc)
            assert doc_id == doc.id
            doc_ids.append(doc_id)
        
        # Verify documents were added
        for doc_id, original_doc in zip(doc_ids, sample_evidence_documents):
            retrieved_doc = store.get_evidence_document_by_id(doc_id)
            assert retrieved_doc is not None
            assert retrieved_doc.evidence == original_doc.evidence
    
    def test_bulk_add_documents(self, test_config, sample_column_documents, sample_sql_documents):
        """Test bulk adding documents."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Combine different document types
        all_docs = sample_column_documents + sample_sql_documents
        
        # Bulk add
        doc_ids = store.bulk_add_documents(all_docs)
        assert len(doc_ids) == len(all_docs)
        
        # Verify all documents were added
        for doc_id, original_doc in zip(doc_ids, all_docs):
            retrieved_doc = store.get_document(doc_id)
            assert retrieved_doc is not None
            assert retrieved_doc.id == original_doc.id
    
    def test_search_similar_columns(self, test_config, sample_column_documents):
        """Test similarity search for column documents."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Add documents
        for doc in sample_column_documents:
            store.add_column_description(doc)
        
        # Search for similar documents
        results = store.search_similar(
            query="user email address",
            doc_type=ThothType.COLUMN_NAME,
            top_k=2,
            score_threshold=0.5
        )
        
        assert len(results) > 0
        assert all(isinstance(doc, ColumnNameDocument) for doc in results)
        
        # Check that email column is in results (should be most relevant)
        column_names = [doc.column_name for doc in results]
        assert "email" in column_names
    
    def test_search_similar_sql(self, test_config, sample_sql_documents):
        """Test similarity search for SQL documents."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Add documents
        for doc in sample_sql_documents:
            store.add_sql(doc)
        
        # Search for similar documents
        results = store.search_similar(
            query="revenue by product category",
            doc_type=ThothType.SQL,
            top_k=2,
            score_threshold=0.5
        )
        
        assert len(results) > 0
        assert all(isinstance(doc, SqlDocument) for doc in results)
    
    def test_delete_document(self, test_config, sample_column_documents):
        """Test document deletion."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Add a document
        doc = sample_column_documents[0]
        doc_id = store.add_column_description(doc)
        
        # Verify it exists
        retrieved = store.get_document(doc_id)
        assert retrieved is not None
        
        # Delete it
        store.delete_document(doc_id)
        
        # Verify it's gone
        retrieved = store.get_document(doc_id)
        assert retrieved is None
    
    def test_delete_collection_by_type(self, test_config, sample_column_documents, sample_sql_documents):
        """Test deleting all documents of a specific type."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Add mixed documents
        for doc in sample_column_documents:
            store.add_column_description(doc)
        for doc in sample_sql_documents:
            store.add_sql(doc)
        
        # Verify both types exist
        columns = store.get_all_column_documents()
        sqls = store.get_all_sql_documents()
        assert len(columns) == len(sample_column_documents)
        assert len(sqls) == len(sample_sql_documents)
        
        # Delete all column documents
        store.delete_collection(ThothType.COLUMN_NAME)
        
        # Verify only SQL documents remain
        columns = store.get_all_column_documents()
        sqls = store.get_all_sql_documents()
        assert len(columns) == 0
        assert len(sqls) == len(sample_sql_documents)
    
    def test_get_all_documents_by_type(self, test_config, sample_column_documents, sample_sql_documents, sample_evidence_documents):
        """Test getting all documents by type."""
        store = VectorStoreFactory.from_config(test_config)
        
        # Add all document types
        for doc in sample_column_documents:
            store.add_column_description(doc)
        for doc in sample_sql_documents:
            store.add_sql(doc)
        for doc in sample_evidence_documents:
            store.add_evidence(doc)
        
        # Get all documents by type
        columns = store.get_all_column_documents()
        sqls = store.get_all_sql_documents()
        evidences = store.get_all_evidence_documents()
        
        # Verify counts
        assert len(columns) == len(sample_column_documents)
        assert len(sqls) == len(sample_sql_documents)
        assert len(evidences) == len(sample_evidence_documents)
        
        # Verify types
        assert all(isinstance(doc, ColumnNameDocument) for doc in columns)
        assert all(isinstance(doc, SqlDocument) for doc in sqls)
        assert all(isinstance(doc, EvidenceDocument) for doc in evidences)