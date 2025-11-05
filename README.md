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
│  │          Azure App Service                          │   │
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
│  │          Azure App Service (Linux)                  │   │
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
- **Scalability**: Horizontal scaling via App Services
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
- **Deployment**: Azure App Service (Windows/Linux)

### Python RAG API
- **Framework**: FastAPI + Pydantic v2
- **AI/ML**: LangChain, Azure OpenAI SDK
- **Vector Store**: Azure AI Search
- **Document Processing**: pypdf, python-docx, unstructured
- **Deployment**: Azure App Service (Linux)

### Azure Services
- **Compute**: App Services, Static Web Apps
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
# Login to Azure
az login

# Deploy infrastructure
cd infrastructure/bicep
az deployment sub create --location eastus --template-file main.bicep

# Deploy applications
cd ../..
./scripts/deploy-all.sh
```

## 📁 Project Structure

```
document-rag-azure/
├── frontend-react/          # React SPA (Azure SWA)
├── dotnet-gateway/          # .NET API Gateway (App Service)
├── python-rag-api/          # Python RAG API (App Service)
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