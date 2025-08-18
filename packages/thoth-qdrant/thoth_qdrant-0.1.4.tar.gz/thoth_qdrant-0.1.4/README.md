# Thoth Qdrant

A native Qdrant implementation for the Thoth Vector Database system, providing high-performance vector storage and similarity search capabilities without Haystack dependencies.

## Features

- **Native Qdrant Integration**: Direct use of Qdrant client without Haystack
- **Full API Compatibility**: Same interface as thoth_vdb2 for seamless integration
- **External Embeddings**: Support for OpenAI, Cohere, Mistral, and HuggingFace
- **Document Types**: EvidenceDocument, SqlDocument, ColumnNameDocument
- **Similarity Search**: Native Qdrant search with document type filtering
- **Batch Operations**: Efficient bulk document insertion
- **Caching**: Intelligent embedding cache for performance

## Installation

```bash
# Basic installation
pip install thoth-qdrant

# With OpenAI embeddings support
pip install thoth-qdrant[openai]

# With all embedding providers
pip install thoth-qdrant[all-providers]
```

## Configuration

### Environment Variables

```bash
# Embedding provider configuration
export EMBEDDING_PROVIDER=openai
export EMBEDDING_MODEL=text-embedding-3-small
export OPENAI_API_KEY=your-api-key

# Or use provider-specific keys
export OPENAI_API_KEY=sk-...
export COHERE_API_KEY=...
export MISTRAL_API_KEY=...
```

### Qdrant Setup

Ensure Qdrant is running locally:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## Usage

```python
from thoth_qdrant import VectorStoreFactory
from thoth_qdrant.core.base import (
    ColumnNameDocument,
    SqlDocument,
    EvidenceDocument,
    ThothType,
)

# Create vector store
store = VectorStoreFactory.create(
    backend="qdrant",
    collection="my_collection",
    host="localhost",
    port=6333,
    embedding_provider="openai",
    embedding_model="text-embedding-3-small"
)

# Add documents
column_doc = ColumnNameDocument(
    table_name="users",
    column_name="email",
    original_column_name="email_address",
    column_description="User email for authentication",
    value_description="Valid email format"
)
doc_id = store.add_column_description(column_doc)

sql_doc = SqlDocument(
    question="How to find recent users?",
    sql="SELECT * FROM users WHERE created_at > NOW() - INTERVAL '30 days'",
    evidence="Filter by date using interval"
)
store.add_sql(sql_doc)

# Search similar documents
results = store.search_similar(
    query="user email authentication",
    doc_type=ThothType.COLUMN_NAME,
    top_k=5,
    score_threshold=0.7
)

# Bulk operations
documents = [column_doc, sql_doc]
doc_ids = store.bulk_add_documents(documents)

# Get document by ID
doc = store.get_document(doc_id)

# Delete document
store.delete_document(doc_id)

# Get all documents by type
all_columns = store.get_all_column_documents()
all_sql = store.get_all_sql_documents()

# Collection info
info = store.get_collection_info()
print(info)
```

## API Reference

### VectorStoreInterface Methods

- `add_column_description(doc: ColumnNameDocument) -> str`
- `add_sql(doc: SqlDocument) -> str`
- `add_evidence(doc: EvidenceDocument) -> str`
- `search_similar(query: str, doc_type: ThothType, top_k: int = 5, score_threshold: float = 0.7) -> List[BaseThothDocument]`
- `get_document(doc_id: str) -> Optional[BaseThothDocument]`
- `delete_document(doc_id: str) -> None`
- `bulk_add_documents(documents: List[BaseThothDocument]) -> List[str]`
- `delete_collection(thoth_type: ThothType) -> None`
- `get_all_column_documents() -> List[ColumnNameDocument]`
- `get_all_sql_documents() -> List[SqlDocument]`
- `get_all_evidence_documents() -> List[EvidenceDocument]`
- `get_collection_info() -> Dict[str, Any]`

## Testing

```bash
# Run tests with local Qdrant
pytest tests/

# Run specific test
pytest tests/test_qdrant_adapter.py -v

# With coverage
pytest --cov=thoth_qdrant tests/
```

## Development

```bash
# Install development dependencies
pip install -e .[dev,test]

# Format code
black thoth_qdrant tests
isort thoth_qdrant tests

# Type checking
mypy thoth_qdrant

# Linting
ruff thoth_qdrant
```

## License

Apache License 2.0 - See LICENSE.md for details

## Compatibility

This library is fully compatible with thoth_vdb2 API, allowing seamless migration from Haystack-based implementations to native Qdrant.