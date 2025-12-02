README.md
# Document RAG - Azure Cloud Architecture

A production-ready, enterprise-grade Document RAG system built for Azure Cloud, showcasing hybrid .NET + Python capabilities.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          React SPA (TypeScript)                     │   │
│  │          Azure Static Web Apps                      │   │
│  │          • Document Upload UI                       │   │
│  │          • Chat Interface                           │   │
│  │          • Real-time Results Display                │   │
│  └──────────────────────┬──────────────────────────────┘   │
└─────────────────────────┼──────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          .NET Gateway (ASP.NET Core 8)              │   │
│  │          Azure Container Apps                       │   │
│  │          • Authentication & Authorization           │   │
│  │          • Rate Limiting & Throttling               │   │
│  │          • Response Caching (Redis)                 │   │
│  │          • Request Validation                       │   │
│  │          • API Versioning                           │   │
│  │          • Logging & Monitoring                     │   │
│  └──────────────────────┬──────────────────────────────┘   │
└─────────────────────────┼──────────────────────────────────┘
                          │ Internal HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAG PROCESSING LAYER                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       Python RAG API (FastAPI + LangChain)          │   │
│  │          Azure Container Apps                       │   │
│  │          • Document Processing                      │   │
│  │          • Text Chunking & Embedding                │   │
│  │          • Vector Search                            │   │
│  │          • RAG Orchestration                        │   │
│  │          • LLM Integration                          │   │
│  └──────────────────────┬──────────────────────────────┘   │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    AZURE AI SERVICES                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │  Azure OpenAI   │  │  Azure AI       │  │  Blob      │ │
│  │  • GPT-4        │  │  Search         │  │  Storage   │ │
│  │  • Embeddings   │  │  • Vector Store │  │  • Docs    │ │
│  └─────────────────┘  └─────────────────┘  └────────────┘ │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │  Cosmos DB      │  │  Redis Cache    │  │  Key Vault │ │
│  │  • Metadata     │  │  • Session      │  │  • Secrets │ │
│  │  • Conversations│  │  • Results      │  │  • API Keys│ │
│  └─────────────────┘  └─────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Why This Architecture?

### **Demonstrates Both Skills**
- **.NET Gateway**: Enterprise patterns, caching, auth (shows .NET capability)
- **Python RAG**: AI/ML expertise with LangChain (your strength)

### **Production-Grade Features**
- **Security**: Authentication, authorization, API key management
- **Performance**: Redis caching, rate limiting, optimized queries
- **Scalability**: Horizontal scaling via Azure Container Apps
- **Observability**: Application Insights, structured logging
- **Cost-Effective**: Serverless frontend (SWA), auto-scaling backend

## 📦 Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State**: Zustand + TanStack Query
- **Deployment**: Azure Static Web Apps

### .NET Gateway
- **Framework**: ASP.NET Core 8 (Minimal APIs)
- **Auth**: Azure AD B2C / JWT
- **Caching**: Redis (StackExchange.Redis)
- **Rate Limiting**: AspNetCoreRateLimit
- **Deployment**: Azure Container Apps (Linux)

### Python RAG API
- **Framework**: FastAPI + Pydantic v2
- **AI/ML**: LangChain, Azure OpenAI SDK
- **Vector Store**: Azure AI Search
- **Document Processing**: pypdf, python-docx, unstructured
- **Deployment**: Azure Container Apps (Linux)

### Azure Services
- **Compute**: Azure Container Apps, Static Web Apps
- **AI**: Azure OpenAI, Azure AI Search
- **Storage**: Blob Storage, Cosmos DB
- **Caching**: Azure Cache for Redis
- **Security**: Key Vault, Managed Identity
- **Monitoring**: Application Insights, Log Analytics

## 🚀 Quick Start

### Prerequisites
- .NET 8 SDK
- Python 3.11+
- Node.js 20+
- Azure CLI
- Azure Subscription

### Local Development
```bash
# Frontend
cd frontend-react
npm install
npm run dev

# .NET Gateway
cd dotnet-gateway
dotnet restore
dotnet run

# Python RAG API
cd python-rag-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Azure Deployment
```bash
# Login & choose subscription
az login
az account set --subscription <subscription-id>

# Create (or reuse) the resource group
RESOURCE_GROUP=doc-rag
az group create --name $RESOURCE_GROUP --location eastus

# Deploy infrastructure (Gateway + Python APIs + ACR + Static Web App + Redis + Cosmos + Search)
cd infrastructure/bicep
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --template-file main.bicep \
  --parameters tenantId=<your-tenant-id> \
               resourcePrefix=docrag \
               environment=dev \
               location=eastus \
               openAiLocation=eastus \
               deployPythonApi=true \
               deployStaticWebApp=true \
               deploySearch=true \
               staticWebAppLocation=eastus2
cd ../..

# Capture outputs
REGISTRY_LOGIN_SERVER=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query "properties.outputs.containerRegistryLoginServer.value" \
  -o tsv)
RESOURCE_PREFIX=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query "properties.parameters.resourcePrefix.value" \
  -o tsv)
ENVIRONMENT_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query "properties.parameters.environment.value" \
  -o tsv)
PYTHON_CONTAINER_APP=${RESOURCE_PREFIX}-${ENVIRONMENT_NAME}-rag
GATEWAY_CONTAINER_APP=${RESOURCE_PREFIX}-${ENVIRONMENT_NAME}-gateway

# Authenticate docker to ACR (admin disabled)
az acr login --name ${REGISTRY_LOGIN_SERVER%%.*}

# Build & push images
docker build -f dotnet-gateway/Dockerfile -t ${REGISTRY_LOGIN_SERVER}/gateway-api:latest dotnet-gateway
docker push ${REGISTRY_LOGIN_SERVER}/gateway-api:latest

docker build -t ${REGISTRY_LOGIN_SERVER}/python-rag:latest python-rag-api
docker push ${REGISTRY_LOGIN_SERVER}/python-rag:latest

# Update Container Apps to pull the latest image tags
az containerapp update \
  --name $GATEWAY_CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --image ${REGISTRY_LOGIN_SERVER}/gateway-api:latest

az containerapp update \
  --name $PYTHON_CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --image ${REGISTRY_LOGIN_SERVER}/python-rag:latest
```

### CI/CD

- `.github/workflows/deploy-gateway.yml` builds a Docker image for the gateway, pushes it to ACR, and updates the Azure Container App whenever `main` receives changes under `dotnet-gateway/**`.
- The workflow expects an `AZURE_CREDENTIALS` secret (service principal JSON with `Contributor` on the resource group) and uses the parameters in the `env` block (`RESOURCE_GROUP`, `RESOURCE_PREFIX`, `ENVIRONMENT_NAME`, `DEPLOYMENT_NAME`) to locate the right resources.
- A companion workflow for the Python API would follow the same pattern—build the container, push to ACR, and call `az containerapp update` for `${RESOURCE_PREFIX}-${ENVIRONMENT_NAME}-rag`.

### Redeploying After Changes

#### Gateway (.NET)
- Push to `main` and let the `Deploy Gateway API` GitHub Actions workflow rebuild and redeploy automatically.
- To run locally or from CI by hand:
  ```bash
  az acr login --name docrag34noh4zacr
  docker buildx build \
    --platform linux/amd64 \
    -f dotnet-gateway/Dockerfile \
    -t docrag34noh4zacr.azurecr.io/gateway-api:latest \
    dotnet-gateway \
    --push

  az containerapp update \
    --name docrag3-dev-gateway \
    --resource-group doc-rag \
    --image docrag34noh4zacr.azurecr.io/gateway-api:latest
  ```

#### Python RAG API
- (Optional) Create a separate GitHub workflow mirroring the commands below.
- Manual redeploy:
  ```bash
  az acr login --name docrag34noh4zacr
  docker buildx build \
    --platform linux/amd64 \
    -f python-rag-api/Dockerfile \
    -t docrag34noh4zacr.azurecr.io/python-rag:latest \
    python-rag-api \
    --push

  az containerapp update \
    --name docrag3-dev-rag \
    --resource-group doc-rag \
    --image docrag34noh4zacr.azurecr.io/python-rag:latest
  ```

#### Static Web App
- Commits to `main` automatically trigger the Azure-generated build workflow (once the portal workflow file and token are configured).
- If you need to redeploy manually, push to `main` or re-run the GitHub workflow `Azure Static Web Apps CI/CD`.

> **Tip:** the Container Apps expect AMD64 images. Always build with `docker buildx build --platform linux/amd64 … --push` even on Apple Silicon Macs.

## 📁 Project Structure

```
document-rag-azure/
├── frontend-react/          # React SPA (Azure SWA)
├── dotnet-gateway/          # .NET API Gateway (Container App)
├── python-rag-api/          # Python RAG API (Container App)
├── infrastructure/          # IaC (Bicep/Terraform)
├── docs/                    # Documentation
└── .github/workflows/       # CI/CD Pipelines
```

## 🎓 Learning Resources

- [Azure Architecture Center - RAG Pattern](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/rag-solution)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/)

## 💰 Estimated Azure Costs

**Development**: ~$50-100/month
**Production (Low Traffic)**: ~$200-400/month
**Production (Medium Traffic)**: ~$800-1500/month

*See `docs/deployment/COST_ESTIMATION.md` for detailed breakdown*

## 🔒 Security Features

- Azure AD B2C Authentication
- Managed Identity for service-to-service auth
- Key Vault for secrets management
- API rate limiting and throttling
- CORS policies
- Input validation and sanitization

## 📊 Monitoring & Observability

- Application Insights for all services
- Log Analytics workspace
- Custom metrics and alerts
- Distributed tracing
- Real-time dashboards

## 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines.

## 📄 License

MIT License - See `LICENSE` file