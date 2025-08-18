# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Base classes and interfaces for Thoth Vector Database."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator

T = TypeVar('T', bound='BaseThothDocument')


class ThothType(Enum):
    """Supported document types in Thoth."""
    COLUMN_NAME = "column_name"
    EVIDENCE = "evidence"
    SQL = "sql"


class BaseThothDocument(BaseModel):
    """Base class for all Thoth documents."""
    model_config = ConfigDict(use_enum_values=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    thoth_type: ThothType
    text: str = ""


class ColumnNameDocument(BaseThothDocument):
    """Document for column descriptions."""
    table_name: str
    column_name: str
    original_column_name: str
    column_description: str
    value_description: str
    thoth_type: ThothType = ThothType.COLUMN_NAME
    
    @field_validator('table_name', 'column_name', 'original_column_name', 
                     'column_description', 'value_description', mode='before')
    @classmethod
    def sanitize_strings(cls, v):
        """Sanitize string fields by removing excess whitespace and newlines."""
        if isinstance(v, str):
            # Remove leading/trailing whitespace and replace internal newlines with spaces
            return " ".join(v.strip().split())
        return v


class SqlDocument(BaseThothDocument):
    """Document for SQL examples."""
    question: str
    sql: str
    evidence: str = ""
    thoth_type: ThothType = ThothType.SQL
    
    @field_validator('question', 'sql', 'evidence', mode='before')
    @classmethod
    def sanitize_strings(cls, v):
        """Sanitize string fields by removing excess whitespace and newlines."""
        if isinstance(v, str):
            # For SQL, preserve some formatting but clean up excess whitespace
            lines = v.strip().split('\n')
            cleaned_lines = [' '.join(line.split()) for line in lines]
            return ' '.join(cleaned_lines)
        return v


class EvidenceDocument(BaseThothDocument):
    """Document for evidence."""
    evidence: str
    thoth_type: ThothType = ThothType.EVIDENCE
    
    @field_validator('evidence', mode='before')
    @classmethod
    def sanitize_evidence(cls, v):
        """Sanitize evidence field by removing excess whitespace and newlines."""
        if isinstance(v, str):
            return " ".join(v.strip().split())
        return v


class VectorStoreInterface(ABC, Generic[T]):
    """Interface for vector store implementations."""

    @abstractmethod
    def add_column_description(self, doc: ColumnNameDocument) -> str:
        """Add a column description document."""
        pass

    @abstractmethod
    def add_sql(self, doc: SqlDocument) -> str:
        """Add an SQL document."""
        pass

    @abstractmethod
    def add_evidence(self, doc: EvidenceDocument) -> str:
        """Add an evidence document."""
        pass

    @abstractmethod
    def search_similar(
        self,
        query: str,
        doc_type: ThothType,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> list[BaseThothDocument]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[BaseThothDocument]:
        """Get a document by ID."""
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """Delete a document by ID."""
        pass

    @abstractmethod
    def get_collection_info(self) -> dict[str, Any]:
        """Get collection information."""
        pass

    @abstractmethod
    def bulk_add_documents(self, documents: list[BaseThothDocument], policy: Optional[str] = None) -> list[str]:
        """Add multiple documents in batch."""
        pass

    @abstractmethod
    def delete_collection(self, thoth_type: ThothType) -> None:
        """Delete all documents of a specific type."""
        pass

    def get_all_column_documents(self) -> list[ColumnNameDocument]:
        """Get all column documents."""
        return [
            doc for doc in self._get_all_documents()
            if isinstance(doc, ColumnNameDocument)
        ]

    def get_all_sql_documents(self) -> list[SqlDocument]:
        """Get all SQL documents."""
        return [
            doc for doc in self._get_all_documents()
            if isinstance(doc, SqlDocument)
        ]

    def get_all_evidence_documents(self) -> list[EvidenceDocument]:
        """Get all evidence documents."""
        return [
            doc for doc in self._get_all_documents()
            if isinstance(doc, EvidenceDocument)
        ]

    def get_columns_document_by_id(self, doc_id: str) -> Optional[ColumnNameDocument]:
        """Get a column document by ID."""
        doc = self.get_document(doc_id)
        return doc if isinstance(doc, ColumnNameDocument) else None

    def get_sql_document_by_id(self, doc_id: str) -> Optional[SqlDocument]:
        """Get an SQL document by ID."""
        doc = self.get_document(doc_id)
        return doc if isinstance(doc, SqlDocument) else None

    def get_evidence_document_by_id(self, doc_id: str) -> Optional[EvidenceDocument]:
        """Get an evidence document by ID."""
        doc = self.get_document(doc_id)
        return doc if isinstance(doc, EvidenceDocument) else None

    @abstractmethod
    def _get_all_documents(self) -> list[BaseThothDocument]:
        """Get all documents (internal method)."""
        pass