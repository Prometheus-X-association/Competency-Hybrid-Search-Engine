# Competency Hybrid Search Engine

[![Python](https://img.shields.io/badge/Python-FFD43B?logo=python)](https://www.python.org/)
![License](https://img.shields.io/badge/GPL--3.0-red?logo=gnu)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-E6F0FF?logo=githubactions)](https://github.com/features/actions)
[![Pytest](https://img.shields.io/badge/pytest-E6F7FF?logo=pytest)](https://docs.pytest.org/)
[![EditorConfig](https://img.shields.io/badge/EditorConfig-333333?logo=editorconfig)](https://editorconfig.org/)
[![Rye](https://img.shields.io/badge/Rye-000000?logo=rye)](https://rye.astral.sh/)
[![Ruff](https://img.shields.io/badge/Ruff-3A3A3A?logo=ruff)](https://docs.astral.sh/ruff/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-40332E?logo=pre-commit)](https://pre-commit.com/)
[![Makefile](https://img.shields.io/badge/Makefile-427819?logo=gnu)](https://www.gnu.org/software/make/manual/make.html)
[![MkDocs](https://img.shields.io/badge/MkDocs-526CFE?logo=markdown)](https://www.mkdocs.org/)

## Overview

The Competency Hybrid Search Engine is a powerful, modern search system designed for indexing, managing, and searching competencies and skills data. Built with FastAPI and Qdrant vector database, it provides both traditional keyword search (sparse) and semantic search (dense) capabilities using state-of-the-art embedding models.

For more information about this project, see the [Related Work section](./RELATED_WORK.md) and the [Specifications](./SPECIFICATIONS.md).

### Key Features

- **Hybrid Search**: Combines sparse keyword search with dense semantic vector search for optimal results
- **Multi-language Support**: Handles competency data in multiple languages with advanced multilingual models
- **Standard Data Formats**: Compatible with any skill dataset format; examples for ESCO (European Skills, Competences, Qualifications and Occupations), ROME (French job classification), and FORMA datasets provided
- **REST API**: Clean, well-documented FastAPI interface for easy integration
- **Advanced Embeddings**: Uses Qwen3-Embedding-0.6B for dense vectors and OpenSearch neural sparse encoding for sparse vectors
- **Clean Architecture**: Domain-driven design with clear separation of concerns and dependency inversion
- **100% Test Coverage**: Comprehensive test suite with full coverage across all components
- **Production Ready**: Containerized deployment with Docker, Traefik reverse proxy, and monitoring

## Setup and installation

### Prerequisites

- Python 3.13 or higher
- [Rye](https://rye.astral.sh) for dependency management
- Docker and Docker Compose (for containerized deployment)
- Git

### Installation

#### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd competency-hybrid-search-engine
   ```

2. **Initialize the project**
   ```bash
   make init
   ```
   This command will:
   - Check if Rye is installed
   - Install dependencies
   - Set up pre-commit hooks
   - Create environment file from template

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Install dependencies**
   ```bash
   make install
   ```

#### Docker Deployment

1. **Development environment**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml build
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

2. **Production environment**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## Usage

### Starting the Services

#### Local Development

1. **Start the search engine API**
   ```bash
   rye run start
   ```
   The API will be available at `http://localhost:8005`

2. **Start the data importer service**
   ```bash
   rye run start-data-importer
   ```
   The data importer will be available at `http://localhost:8006`

#### Using Docker

1. **Development environment with Traefik**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

2. **Production environment**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

The services will be available at:
- Search Engine API: `http://search-engine.localhost` (dev) or configured domain
- Data Importer: `http://data-importer.localhost` (dev) or configured domain  
- Qdrant Dashboard: `http://qdrant.localhost` (dev) or configured domain
- Traefik Dashboard: `http://localhost:8080` (dev only)

### API Endpoints

#### Search Endpoints
- `POST /search/text`: Perform hybrid, semantic, or sparse search queries with filtering support

#### Entity Management
- `POST /entities`: Add new competency entities
- `GET /entities/{id}`: Retrieve specific entity
- `PUT /entities/{id}`: Update entity
- `DELETE /entities/{id}`: Delete entity

#### Data Import
- `POST /import`: Unified endpoint with a `provider` parameter, to import a raw skill
- `POST /import/file`: Import raw skills from a JSON array file

#### Interactive API Documentation

Once the services are running, access the interactive API documentation:
- **Swagger UI**: `http://search-engine.localhost/docs` (for search engine) or `http://data-importer.localhost/docs` (for data importer)
- **ReDoc**: `http://search-engine.localhost/redoc` (for search engine) or `http://data-importer.localhost/redoc` (for data importer)

### Example Usage

```python
import requests

# Hybrid search for skills related to "programming"
response = requests.post(
    "http://search-engine.localhost/search/text",
    json={
        "text": "programming",
        "search_type": "hybrid",  # or "semantic" or "sparse"
        "top": 10,
        "filters": [
            {
                "field": "category",
                "operator": "eq",
                "value": "Information Technology"
            }
        ]
    }
)
results = response.json()

# Add a new competency
new_competency = {
    "competency": {
        "code": "PROG_001",
        "title": "Python Programming",
        "description": "Ability to write and maintain Python applications",
        "category": "Information Technology",
        "lang": "en",
        "type": "skill",
        "provider": "esco"
    }
}
response = requests.post(
    "http://search-engine.localhost/entities",
    json=new_competency
)
```

**Example Search Response:**
```json
{
  "results": [
    {
      "identifier": "123e4567-e89b-12d3-a456-426614174000",
      "competency": {
        "code": "S1.2.3",
        "title": "Python Programming",
        "description": "Develop software using Python language",
        "lang": "en",
        "type": "skill",
        "provider": "esco",
        "category": "Information Technology"
      },
      "score": 0.92
    },
    {
      "identifier": "987fcdeb-51a2-43c7-b789-123456789abc",
      "competency": {
        "code": "S2.1.5",
        "title": "Software Development",
        "lang": "en",
        "type": "skill",
        "provider": "esco"
      },
      "score": 0.87
    }
  ]
}
```

**Example Entity Response:**
```json
{
  "identifier": "123e4567-e89b-12d3-a456-426614174000",
  "competency": {
    "code": "PROG_001",
    "title": "Python Programming",
    "description": "Ability to write and maintain Python applications",
    "category": "Information Technology",
    "lang": "en",
    "type": "skill",
    "provider": "esco"
  }
}
```

#### Error Responses

All errors follow this standard format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `400 Bad Request`: Invalid parameters or malformed request
- `404 Not Found`: Entity with specified ID doesn't exist
- `422 Validation Error`: Invalid request body or field values
- `500 Internal Server Error`: Server-side error occurred

**Example Error Response:**
```json
{
  "detail": "Entity not found with identifier: 123e4567-e89b-12d3-a456-426614174000"
}
```

### Advanced Usage

For advanced search features, see:

- **[Search Scores Guide](./SEARCH_SCORES.md)** - Understanding similarity scores (Cosine, BM25, RRF) and when to use each search type
- **[Search Filters Reference](./SEARCH_FILTERS.md)** - Filtering results with operators and field-based criteria

## Development

### Development Workflow

1. **Code formatting and linting**
   ```bash
   make format  # Format code with Ruff
   make lint    # Run linting checks
   ```

2. **Running tests**
   ```bash
   make test           # Run all tests with coverage
   make diff-cover     # Show coverage for recent changes
   ```

3. **Pre-commit checks**
   ```bash
   make precommit      # Run all pre-commit hooks
   make check          # Run precommit + tests
   ```

4. **Complete build**
   ```bash
   make all           # Format, lint, and test everything
   ```

### Code Formatting and Linting

The project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter and formatter
- **Pre-commit**: Git hooks for code quality checks
- **Pytest**: Testing framework with coverage reporting

Configuration files:
- `.pre-commit-config.yaml`: Pre-commit hook configuration
- `pyproject.toml`: Python project configuration and tool settings

### Environment Variables

#### General Configuration

| Variable | Description | Required | Default Value | Possible Values |
|----------|-------------|----------|---------------|-----------------|
| `ENVIRONMENT` | Deployment environment | No | `development` | `development`, `staging`, `production` |
| `LOG_LEVEL` | Application logging level | No | `DEBUG` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `PYTHONPATH` | Python module search paths | No | `.:./src:./src/search_engine:./src/data_importer` | Colon-separated paths |

#### Database Configuration

| Variable | Description | Required | Default Value | Notes |
|----------|-------------|----------|---------------|-------|
| `DB_METHOD` | Database method to use | No | `qdrant` | Currently only supports Qdrant (`qdrant`) |
| `DB_QDRANT_HOST` | Qdrant database host | No | `qdrant` | Any valid hostname/IP |
| `DB_QDRANT_PORT` | Qdrant database port | No | `6333` | Any valid port number |
| `DB_QDRANT_URL` | Qdrant database URL | No | `http://qdrant:6333` | Full URL to Qdrant instance |
| `DB_QDRANT_API_KEY` | Qdrant API key for authentication | No | `None` | Any string or null for no auth |
| `DB_QDRANT_COLLECTION` | Name of the Qdrant collection | No | `entities` | Any valid collection name |
| `DB_QDRANT_VECTOR_DIMENSIONS` | Vector embedding dimensions | No | `1024` | **Must match EMBEDDING_HF_VECTOR_DIMENSIONS** |
| `DB_QDRANT_VECTOR_DISTANCE` | Distance metric for vectors | No | `Cosine` | `Cosine`, `Euclid`, `Dot`, `Manhattan` |
| `DB_QDRANT_DENSE_VECTOR_NAME` | Name of dense vector in collection | No | `dense` | Any valid vector name |
| `DB_QDRANT_SPARSE_VECTOR_NAME` | Name of sparse vector in collection | No | `sparse` | Any valid vector name |

#### Embedding Configuration

| Variable | Description | Required | Default Value | Notes |
|----------|-------------|----------|---------------|-------|
| `EMBEDDING_METHOD` | Embedding method to use | No | `hf` | Currently only supports HuggingFace (`hf`) |
| `EMBEDDING_HF_MODEL_NAME` | Dense embedding model | No | `Qwen/Qwen3-Embedding-0.6B` | Any HuggingFace embedding model |
| `EMBEDDING_HF_VECTOR_DIMENSIONS` | Dense embedding vector dimensions | No | `1024` | **Must match DB_QDRANT_VECTOR_DIMENSIONS** |
| `SPARSE_EMBEDDING_MODEL_NAME` | Sparse embedding model | No | `opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1` | Any sparse embedding model |

#### Service Configuration

| Variable | Description | Required | Default Value | Notes |
|----------|-------------|----------|---------------|-------|
| `SEARCH_ENGINE_HOST` | Search engine service host | No | `search-engine` | Docker service name or hostname |
| `SEARCH_ENGINE_PORT` | Search engine API port | No | `8000` | Any valid port number |
| `SEARCH_ENGINE_ENDPOINT` | Full search engine endpoint URL | No | `http://search-engine:8000/entities` | Used by data importer |
| `DATA_IMPORTER_PORT` | Data importer API port | No | `8000` | Any valid port number |

#### Deployment Configuration (Production)

| Variable | Description | Required | Default Value | Notes |
|----------|-------------|----------|---------------|-------|
| `LETSENCRYPT_EMAIL` | Email for Let's Encrypt certificates | Yes (prod only) | `email@example.com` | Valid email for SSL certificates |
| `SEARCH_ENGINE_DOMAIN_NAME` | Domain for search engine | Yes (prod only) | `search-engine.localhost` | Production domain name |
| `DATA_IMPORTER_DOMAIN_NAME` | Domain for data importer | Yes (prod only) | `data-importer.localhost` | Production domain name |
| `DB_DOMAIN_NAME` | Domain for Qdrant dashboard | Yes (prod only) | `db.localhost` | Production domain name |

#### Gunicorn Configuration

| Variable | Description | Required | Default Value | Notes |
|----------|-------------|----------|---------------|-------|
| `WORKERS_COUNT` | Number of Gunicorn worker processes | No | `min(CPU_count * 2 + 1, 8)` | Auto-scales based on CPU cores, capped at 8 |
| `THREADS_PER_WORKER` | Number of threads per worker process | No | `1` | Increase for CPU-bound tasks. For async applications, 1 thread is usually optimal |
| `WORKER_TIMEOUT` | Worker timeout in seconds | No | `600` | Workers silent for longer than this are killed and restarted |
| `GRACEFUL_TIMEOUT` | Graceful shutdown timeout in seconds | No | `60` | Time to wait for workers to finish handling requests during shutdown before force-killing them |


### Architecture

The application follows a clean architecture pattern with clear separation of concerns:

```
src/
├── search_engine/            # Main search engine application
│   ├── adapters/             # External interfaces (API, DB, etc.)
│   │   ├── api/              # FastAPI REST endpoints
│   │   ├── encoding/         # Embedding services (HuggingFace)
│   │   └── infrastructure/   # Database and external services
│   └── domain/               # Core business logic
│       ├── contracts/        # Interfaces and protocols
│       ├── services/         # Business services
│       └── types/            # Domain models and types
└── data_importer/            # Data ingestion service
    ├── indexing_strategies/  # Data indexing strategies
    └── mappers/              # Data format mappers (ESCO, ROME, FORMA)
```

#### Key Components

1. **Search Engine Core**
   - FastAPI application with automatic OpenAPI documentation
   - Hybrid search combining sparse keyword search and dense semantic search
   - Dense vector embeddings using Sentence Transformers
   - Sparse vector embeddings using Sentence Transformers
   - Qdrant vector database with dual vector storage (dense + sparse)

2. **Architecture Layers**
   - **Domain Layer**: Core business logic, entities, and contracts (Repository, EmbeddingService)
   - **Adapters Layer**: External interfaces (FastAPI routes, Qdrant client, HuggingFace encoders)  
   - **Infrastructure Layer**: Configuration management, database connections, and external services
   - **Dependency Injection**: Constructor-based DI with clear separation of concerns

3. **Data Importer**
   - Separate microservice for bulk data ingestion
   - Support for multiple data formats (ESCO, ROME, FORMA), provided as examples
   - Configurable indexing strategies with vector generation pipeline
   - Data validation and transformation with Pydantic models
   - See [this documentation](./ADD_MAPPER.md) to create and add your own mapper

4. **Infrastructure & DevOps**
   - Docker containerization with multi-stage builds
   - Traefik reverse proxy for production with SSL termination
   - Health checks and monitoring with structured logging (Loguru)
   - 100% test coverage
   - Pre-commit hooks, linting (Ruff), and automated CI/CD

## Contributing

We welcome contributions to this project! Please see
the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to
contribute, including:

- How to set up your development environment
- Coding standards and style guidelines
- Pull request process
- Testing requirements

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Install dependencies: `make init`
4. Make your changes
5. Run tests: `make check`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) -
see the LICENSE file for details.

GPL-3.0 is a strong copyleft license that requires anyone who distributes your
code or a derivative work to make the source available under the same terms.
