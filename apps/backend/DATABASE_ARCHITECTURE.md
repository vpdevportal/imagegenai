# Database Architecture - ImageGenAI

## Professional Structure Overview

This document describes the clean, professional database architecture implemented for storing unique prompts with thumbnail images using SQLite and BLOB storage.

## Architecture Layers

```
app/
├── db/                    # Database layer
│   ├── __init__.py
│   └── connection.py      # SQLite connection & schema
├── models/               # Data models
│   ├── __init__.py
│   └── prompt.py         # Prompt data model
├── schemas/              # API schemas
│   ├── __init__.py
│   └── prompt.py         # Pydantic schemas
├── repositories/         # Data access layer
│   ├── __init__.py
│   └── prompt_repository.py  # Repository pattern
├── services/             # Business logic layer
│   ├── __init__.py
│   └── prompt_service.py     # Service layer
├── utils/                # Utilities
│   ├── __init__.py
│   └── thumbnail.py      # Thumbnail generation
├── api/                  # API endpoints
│   ├── prompts.py        # Prompt API endpoints
│   └── routes.py         # Main router
└── examples/             # Usage examples
    ├── __init__.py
    └── database_integration.py
```

## Layer Responsibilities

### 1. Database Layer (`db/`)
- **Connection Management**: SQLite connection with proper error handling
- **Schema Definition**: Table creation and indexing
- **Connection Pooling**: Context managers for safe connections

### 2. Models Layer (`models/`)
- **Data Models**: Pure Python dataclasses for business entities
- **Business Logic**: Prompt normalization and hashing
- **Type Safety**: Clear data structure definitions

### 3. Schemas Layer (`schemas/`)
- **API Validation**: Pydantic models for request/response validation
- **Serialization**: JSON serialization for API responses
- **Documentation**: Auto-generated API documentation

### 4. Repository Layer (`repositories/`)
- **Data Access**: Clean interface to database operations
- **Query Abstraction**: SQL queries encapsulated in methods
- **Error Handling**: Database-specific error handling

### 5. Service Layer (`services/`)
- **Business Logic**: Complex operations and workflows
- **Integration**: Combines multiple repositories and utilities
- **Validation**: Business rule validation

### 6. API Layer (`api/`)
- **HTTP Endpoints**: RESTful API endpoints
- **Request Handling**: Input validation and error responses
- **Response Formatting**: Consistent API responses

## Database Schema

### Prompts Table
```sql
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_text TEXT NOT NULL,
    prompt_hash TEXT NOT NULL UNIQUE,
    total_uses INTEGER NOT NULL DEFAULT 1,
    first_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model TEXT,
    thumbnail_data BLOB,
    thumbnail_mime TEXT,
    thumbnail_width INTEGER,
    thumbnail_height INTEGER
);
```

### Indexes
- `idx_prompts_hash` - Unique index on prompt_hash
- `idx_prompts_last_used` - Index on last_used_at DESC
- `idx_prompts_total_uses` - Index on total_uses DESC
- `idx_prompts_model` - Index on model

## Key Features

### 1. Prompt Normalization
- Unicode normalization (NFKC)
- Case-insensitive comparison
- Whitespace normalization
- SHA256 hashing for uniqueness

### 2. Thumbnail Storage
- **BLOB Storage**: Thumbnails stored as binary data in SQLite
- **WebP Format**: Optimized compression (~25KB per thumbnail)
- **Metadata**: Width, height, and MIME type stored
- **Generation**: Automatic thumbnail creation from source images

### 3. Usage Tracking
- **Counters**: Track total uses per prompt
- **Timestamps**: First and last usage tracking
- **Model Tracking**: Optional model-specific tracking

### 4. Search & Filtering
- **Full-text Search**: Search across prompt text
- **Model Filtering**: Filter by AI model
- **Sorting**: By popularity or recency
- **Pagination**: Efficient large dataset handling

## API Endpoints

### Prompt Management
- `GET /api/prompts/` - List prompts with pagination
- `GET /api/prompts/search` - Search prompts
- `GET /api/prompts/popular` - Most popular prompts
- `GET /api/prompts/recent` - Recently used prompts
- `GET /api/prompts/{id}` - Get specific prompt
- `GET /api/prompts/{id}/thumbnail` - Get thumbnail image
- `DELETE /api/prompts/{id}` - Delete prompt

### Statistics & Maintenance
- `GET /api/prompts/stats/overview` - Database statistics
- `POST /api/prompts/cleanup` - Clean up old prompts

## Usage Examples

### Basic Usage
```python
from app.services.prompt_service import prompt_service

# Create/update prompt with thumbnail
response = prompt_service.create_or_update_prompt(
    prompt_text="A beautiful sunset over mountains",
    model="gemini-2.5-flash-image-preview",
    image_path="/path/to/generated/image.png"
)

print(f"Prompt ID: {response.id}")
print(f"Total uses: {response.total_uses}")
```

### Search Prompts
```python
# Search for prompts
results = prompt_service.search_prompts("sunset", limit=10)
for prompt in results:
    print(f"{prompt.prompt_text} ({prompt.total_uses} uses)")
```

### Get Statistics
```python
# Get database statistics
stats = prompt_service.get_stats()
print(f"Total prompts: {stats.total_prompts}")
print(f"Total uses: {stats.total_uses}")
```

## Performance Characteristics

### SQLite BLOB Storage
- **Capacity**: Up to ~50k thumbnails (~1GB total)
- **Performance**: Fast for read operations
- **Concurrency**: Single writer, multiple readers
- **Backup**: Single file backup/restore

### Optimization Features
- **Indexed Queries**: All common query patterns indexed
- **Efficient Thumbnails**: WebP format with optimal compression
- **Connection Management**: Proper connection lifecycle
- **Batch Operations**: Transaction support for multiple operations

## Integration with Image Generation

### Service Integration
```python
# In your image generation service
from app.services.prompt_service import prompt_service

def generate_image_with_storage(prompt: str, image_data: bytes):
    # Generate image (your existing logic)
    generated_image = your_image_generation_logic(prompt)
    
    # Save to database with thumbnail
    prompt_record = prompt_service.create_or_update_prompt(
        prompt_text=prompt,
        model="your-model",
        image_data=generated_image
    )
    
    return generated_image, prompt_record
```

### API Integration
```python
# Add to your existing API
from app.api.prompts import router as prompts_router

# Include in your main router
app.include_router(prompts_router)
```

## Maintenance & Monitoring

### Regular Tasks
1. **Monitor Database Size**: Check `data/prompts.db` file size
2. **Cleanup Old Data**: Remove prompts without thumbnails
3. **Backup Database**: Regular backups of SQLite file
4. **Check Statistics**: Monitor usage patterns

### Health Monitoring
```python
# Check database health
stats = prompt_service.get_stats()
print(f"Database size: {stats.total_prompts} prompts")
print(f"Total uses: {stats.total_uses}")
```

## Error Handling

### Comprehensive Error Handling
- **Database Errors**: Connection and query error handling
- **Validation Errors**: Input validation with clear messages
- **Thumbnail Errors**: Graceful fallback when thumbnail generation fails
- **Logging**: Detailed logging for debugging

### Error Recovery
- **Connection Retry**: Automatic retry for transient errors
- **Graceful Degradation**: Continue operation without thumbnails if needed
- **Data Integrity**: Transaction rollback on errors

## Testing

### Run Examples
```bash
cd apps/backend
python -m app.examples.database_integration
```

### Test API Endpoints
```bash
# Start the server
uvicorn main:app --reload

# Test endpoints
curl http://localhost:8000/api/prompts/stats/overview
curl http://localhost:8000/api/prompts/popular
```

## Future Enhancements

### Potential Improvements
- **Vector Search**: Semantic similarity search using embeddings
- **Caching**: Redis cache for frequently accessed data
- **Analytics**: More detailed usage analytics
- **Migration**: Easy migration to PostgreSQL for scale
- **Backup**: Automated backup strategies

### Scaling Considerations
- **PostgreSQL Migration**: For larger deployments
- **Object Storage**: S3/MinIO for thumbnail storage
- **Read Replicas**: For read-heavy workloads
- **Microservices**: Separate database service

This architecture provides a clean, maintainable, and scalable foundation for prompt management with professional separation of concerns and comprehensive error handling.
