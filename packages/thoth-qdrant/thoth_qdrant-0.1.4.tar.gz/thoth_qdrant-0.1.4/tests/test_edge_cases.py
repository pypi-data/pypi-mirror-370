# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Tests for edge cases and input sanitization."""

import pytest
from thoth_qdrant.core.base import (
    ColumnNameDocument,
    SqlDocument,
    EvidenceDocument,
    ThothType,
)
from thoth_qdrant.adapter.qdrant_native import QdrantNativeAdapter


class TestInputSanitization:
    """Test input sanitization for documents with problematic content."""
    
    def test_column_name_with_newlines(self):
        """Test that column names with newlines are properly sanitized."""
        doc = ColumnNameDocument(
            table_name="users\ntable",
            column_name="\n  column_name\n  ",
            original_column_name="  original\nname  ",
            column_description="Description\nwith\nnewlines",
            value_description="Value\n\ndescription"
        )
        
        # Check that fields are sanitized
        assert doc.table_name == "users table"
        assert doc.column_name == "column_name"
        assert doc.original_column_name == "original name"
        assert doc.column_description == "Description with newlines"
        assert doc.value_description == "Value description"
    
    def test_sql_document_with_formatting(self):
        """Test SQL documents with formatting and newlines."""
        doc = SqlDocument(
            question="\n\nHow to find\nusers?\n",
            sql="""
                SELECT *
                FROM   users
                WHERE  created_at > NOW()
            """,
            evidence="  Evidence\n  with\n  spaces  "
        )
        
        # Check sanitization
        assert doc.question == "How to find users?"
        assert "SELECT" in doc.sql
        assert "FROM" in doc.sql
        assert doc.evidence == "Evidence with spaces"
    
    def test_evidence_with_whitespace(self):
        """Test evidence documents with excessive whitespace."""
        doc = EvidenceDocument(
            evidence="\n\n   Use   indexes   for   better   performance   \n\n"
        )
        
        assert doc.evidence == "Use indexes for better performance"
    
    def test_empty_and_null_values(self):
        """Test handling of empty and null values."""
        # Test with empty strings
        doc = ColumnNameDocument(
            table_name="",
            column_name="test",
            original_column_name="",
            column_description="",
            value_description=""
        )
        
        assert doc.table_name == ""
        assert doc.column_name == "test"
        assert doc.original_column_name == ""
    
    def test_special_characters(self):
        """Test handling of special characters."""
        doc = ColumnNameDocument(
            table_name="users_table",
            column_name="email@address",
            original_column_name="email_addr",
            column_description="User's email-address (primary)",
            value_description="Format: user@domain.com"
        )
        
        # Special characters should be preserved
        assert "@" in doc.column_name
        assert "'" in doc.column_description
        assert "@" in doc.value_description
    
    def test_json_like_input(self):
        """Test handling of JSON-like formatted input."""
        # Simulate input that might come from JSON with formatting
        json_formatted_column = '''
        {
            "column_name": "user_id"
        }
        '''
        
        # When parsed, the column_name would be extracted as "user_id"
        # but if the whole JSON string is passed, it should be sanitized
        doc = ColumnNameDocument(
            table_name="users",
            column_name="user_id",  # Already extracted from JSON
            original_column_name="id",
            column_description='{"desc": "User ID"}',  # JSON string in description
            value_description="Integer"
        )
        
        # JSON string should be sanitized to single line
        assert doc.column_description == '{"desc": "User ID"}'


class TestAdapterSanitization:
    """Test sanitization in the adapter."""
    
    def test_sanitize_string_method(self):
        """Test the _sanitize_string method."""
        adapter = QdrantNativeAdapter(
            collection="test",
            host="localhost",
            port=6333,
            embedding_provider="openai",
            embedding_model="text-embedding-3-small"
        )
        
        # Test various inputs
        assert adapter._sanitize_string("  test  ") == "test"
        assert adapter._sanitize_string("\ntest\n") == "test"
        assert adapter._sanitize_string("test\nwith\nnewlines") == "test with newlines"
        assert adapter._sanitize_string("  multiple   spaces  ") == "multiple spaces"
        assert adapter._sanitize_string("") == ""
        assert adapter._sanitize_string(None) == ""
    
    def test_enrich_content_sanitization(self):
        """Test that _enrich_content properly sanitizes."""
        adapter = QdrantNativeAdapter(
            collection="test",
            host="localhost",
            port=6333,
            embedding_provider="openai",
            embedding_model="text-embedding-3-small"
        )
        
        # Create document with problematic content
        doc = ColumnNameDocument(
            table_name="\nusers\n",
            column_name="  email  ",
            original_column_name="email_address",
            column_description="User\nemail",
            value_description="Email\nformat"
        )
        
        enriched = adapter._enrich_content(doc)
        
        # Check that enriched content is properly formatted
        assert "Table: users" in enriched
        assert "Column: email" in enriched
        assert "\n" not in enriched  # No newlines in enriched content
    
    def test_payload_conversion_with_problematic_data(self):
        """Test payload to document conversion with problematic data."""
        adapter = QdrantNativeAdapter(
            collection="test",
            host="localhost",
            port=6333,
            embedding_provider="openai",
            embedding_model="text-embedding-3-small"
        )
        
        # Create payload with problematic data
        payload = {
            "thoth_type": "column_name",
            "thoth_id": "test-id",
            "text": "enriched text",
            "table_name": "\n  users\n  ",
            "column_name": "\n\"column_name\"",  # The problematic case from the error
            "original_column_name": "  col_name  ",
            "column_description": "Description\nwith\nnewlines",
            "value_description": "  Value  "
        }
        
        doc = adapter._payload_to_document(payload)
        
        assert doc is not None
        assert doc.table_name == "users"
        assert doc.column_name == '"column_name"'  # Quotes preserved, whitespace removed
        assert doc.original_column_name == "col_name"
        assert doc.column_description == "Description with newlines"
        assert doc.value_description == "Value"


class TestErrorHandling:
    """Test error handling for edge cases."""
    
    def test_invalid_thoth_type(self):
        """Test handling of invalid thoth_type."""
        adapter = QdrantNativeAdapter(
            collection="test",
            host="localhost",
            port=6333,
            embedding_provider="openai",
            embedding_model="text-embedding-3-small"
        )
        
        payload = {
            "thoth_type": "invalid_type",
            "thoth_id": "test-id",
            "text": "test"
        }
        
        doc = adapter._payload_to_document(payload)
        assert doc is None  # Should return None for invalid type
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        adapter = QdrantNativeAdapter(
            collection="test",
            host="localhost",
            port=6333,
            embedding_provider="openai",
            embedding_model="text-embedding-3-small"
        )
        
        # Payload missing column_name
        payload = {
            "thoth_type": "column_name",
            "thoth_id": "test-id",
            "text": "test",
            "table_name": "users",
            # column_name missing
        }
        
        doc = adapter._payload_to_document(payload)
        # Should handle gracefully with empty string
        assert doc is not None
        assert doc.column_name == ""  # Default to empty string