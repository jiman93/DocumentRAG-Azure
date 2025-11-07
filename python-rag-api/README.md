# Python RAG API

FastAPI + LangChain-based RAG API optimized for Azure OpenAI and Azure AI Search.

## Features

- ✅ **Document Processing**: PDF, DOCX, TXT parsing
- ✅ **Smart Chunking**: Semantic text splitting with overlap
- ✅ **Azure OpenAI**: GPT-4 and embeddings integration
- ✅ **Azure AI Search**: Vector store with hybrid search
- ✅ **Azure Blob Storage**: Document persistence
- ✅ **Cosmos DB**: Metadata and conversation storage
- ✅ **Streaming Responses**: Real-time LLM outputs
- ✅ **Source Citations**: Track and return document sources

## Tech Stack

- **Framework**: FastAPI 0.104+
- **AI/ML**: LangChain, Azure OpenAI SDK
- **Vector Store**: Azure AI Search (Cognitive Search)
- **Document Storage**: Azure Blob Storage
- **Database**: Azure Cosmos DB
- **Processing**: pypdf, python-docx, unstructured

## Project Structure

```
python-rag-api/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── documents.py     # Document upload/management
│   │       ├── chat.py          # RAG query endpoints
│   │       └── health.py        # Health checks
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   └── azure_clients.py    # Azure SDK clients
│   ├── services/
│   │   ├── document_processor.py  # Document parsing & chunking
│   │   ├── embedding_service.py   # Azure OpenAI embeddings
│   │   ├── vector_store.py        # Azure AI Search operations
│   │   ├── rag_service.py         # RAG orchestration
│   │   └── storage_service.py     # Blob & Cosmos operations
│   ├── models/
│   │   ├── document.py         # Document schemas
│   │   └── chat.py             # Chat schemas
│   └── utils/
│       ├── file_utils.py       # File handling
│       └── text_utils.py       # Text processing
├── tests/
├── main.py
└── requirements.txt
```

## Quick Start

### Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# Run the API
python main.py

# API available at: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/unit/test_document_processor.py -v
```

## Configuration

### Environment Variables
```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-key
AZURE_SEARCH_INDEX_NAME=documents-index

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER_NAME=documents

# Azure Cosmos DB
COSMOS_DB_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_DB_KEY=your-key
COSMOS_DB_DATABASE=rag-db
COSMOS_DB_CONTAINER=documents

# RAG Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
TEMPERATURE=0.7
MAX_TOKENS=2000
```

## API Endpoints

### Health
- `GET /health` - Health check
- `GET /health/dependencies` - Check Azure services

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document

### Chat
- `POST /api/v1/chat` - Ask question (RAG query)
- `POST /api/v1/chat/stream` - Streaming responses
- `GET /api/v1/chat/history/{conversation_id}` - Get history

## RAG Pipeline

```
1. Document Upload
   ↓
2. Text Extraction (pypdf/python-docx)
   ↓
3. Smart Chunking (RecursiveCharacterTextSplitter)
   ↓
4. Generate Embeddings (Azure OpenAI)
   ↓
5. Store in Azure AI Search + Blob Storage
   ↓
6. Save Metadata to Cosmos DB

Query Flow:
1. User Question
   ↓
2. Generate Question Embedding
   ↓
3. Vector Search (Azure AI Search)
   ↓
4. Build Context Prompt
   ↓
5. LLM Generation (Azure OpenAI GPT-4)
   ↓
6. Return Answer + Sources
```

## Azure Services Setup

### 1. Azure OpenAI
```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name rag-openai \
  --resource-group rg-rag \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Deploy GPT-4 model
az cognitiveservices account deployment create \
  --name rag-openai \
  --resource-group rg-rag \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

### 2. Azure AI Search
```bash
# Create Azure AI Search service
az search service create \
  --name rag-search \
  --resource-group rg-rag \
  --sku standard \
  --location eastus
```

### 3. Azure Blob Storage
```bash
# Create storage account
az storage account create \
  --name ragstorage \
  --resource-group rg-rag \
  --location eastus \
  --sku Standard_LRS

# Create container
az storage container create \
  --name documents \
  --account-name ragstorage
```

### 4. Cosmos DB
```bash
# Create Cosmos DB account
az cosmosdb create \
  --name rag-cosmos \
  --resource-group rg-rag

# Create database and container
az cosmosdb sql database create \
  --account-name rag-cosmos \
  --resource-group rg-rag \
  --name rag-db

az cosmosdb sql container create \
  --account-name rag-cosmos \
  --resource-group rg-rag \
  --database-name rag-db \
  --name documents \
  --partition-key-path "/id"
```

## Deployment

### Azure App Service
```bash
# Create App Service Plan (Linux)
az appservice plan create \
  --name rag-api-plan \
  --resource-group rg-rag \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name python-rag-api \
  --resource-group rg-rag \
  --plan rag-api-plan \
  --runtime "PYTHON:3.11"

# Deploy code
az webapp up \
  --name python-rag-api \
  --resource-group rg-rag
```

## Performance Optimization

- **Caching**: Embeddings cached to reduce API calls
- **Batch Processing**: Documents processed in batches
- **Connection Pooling**: Reuse Azure SDK clients
- **Async Operations**: Non-blocking I/O throughout
- **Streaming**: Large responses streamed to client

## Monitoring

- Application Insights for telemetry
- Custom metrics for RAG performance
- Query latency tracking
- Token usage monitoring
- Error rate alerts

## Cost Optimization

- Use appropriate Azure OpenAI TPM limits
- Cache embeddings and frequent queries
- Implement smart chunking to reduce token usage
- Use Azure AI Search efficiently
- Monitor and optimize storage costs
