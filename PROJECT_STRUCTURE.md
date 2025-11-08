document-rag-azure/
│
├── README.md                          # Main project overview
├── QUICKSTART.md                      # Quick start guide
├── PROJECT_STRUCTURE.md               # This file
│
├── frontend-react/                    # React Frontend (Azure Static Web Apps)
│   ├── README.md
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── public/
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── components/                # Reusable UI components
│       │   ├── DocumentUpload.tsx
│       │   ├── ChatInterface.tsx
│       │   ├── MessageList.tsx
│       │   └── SourceCitation.tsx
│       ├── pages/                     # Page components
│       │   ├── Home.tsx
│       │   ├── Documents.tsx
│       │   └── Chat.tsx
│       ├── hooks/                     # Custom React hooks
│       │   ├── useDocuments.ts
│       │   ├── useChat.ts
│       │   └── useWebSocket.ts
│       ├── services/                  # API integration
│       │   ├── api.ts
│       │   ├── documentService.ts
│       │   └── chatService.ts
│       ├── store/                     # State management (Zustand)
│       │   ├── documentStore.ts
│       │   └── chatStore.ts
│       ├── types/                     # TypeScript types
│       │   ├── document.ts
│       │   └── chat.ts
│       └── utils/                     # Utilities
│           └── formatters.ts
│
├── dotnet-gateway/                    # .NET API Gateway (App Service)
│   ├── README.md
│   ├── Gateway.sln                    # Solution file
│   │
│   ├── src/
│   │   ├── Gateway.Api/               # Main API project
│   │   │   ├── Gateway.Api.csproj
│   │   │   ├── Program.cs             # Application entry point
│   │   │   ├── appsettings.json       # Configuration
│   │   │   │
│   │   │   ├── Controllers/
│   │   │   │   ├── DocumentsController.cs
│   │   │   │   ├── ChatController.cs
│   │   │   │   └── HealthController.cs
│   │   │   │
│   │   │   ├── Middleware/
│   │   │   │   ├── CachingMiddleware.cs
│   │   │   │   ├── RateLimitingMiddleware.cs
│   │   │   │   └── ExceptionHandlingMiddleware.cs
│   │   │   │
│   │   │   ├── Services/
│   │   │   │   ├── PythonApiProxyService.cs
│   │   │   │   ├── CacheService.cs
│   │   │   │   └── AuthenticationService.cs
│   │   │   │
│   │   │   ├── Models/
│   │   │   │   ├── DocumentDto.cs
│   │   │   │   ├── ChatRequestDto.cs
│   │   │   │   └── ChatResponseDto.cs
│   │   │   │
│   │   │   └── Configuration/
│   │   │       ├── GatewaySettings.cs
│   │   │       ├── RedisSettings.cs
│   │   │       └── RateLimitSettings.cs
│   │   │
│   │   └── Gateway.Core/              # Shared library
│   │       ├── Gateway.Core.csproj
│   │       ├── Interfaces/
│   │       │   ├── ICacheService.cs
│   │       │   └── IProxyService.cs
│   │       ├── Extensions/
│   │       │   ├── ServiceCollectionExtensions.cs
│   │       │   └── HttpContextExtensions.cs
│   │       └── Utils/
│   │           └── JsonHelper.cs
│   │
│   └── tests/
│       ├── Gateway.Api.Tests/         # Unit tests
│       │   ├── Gateway.Api.Tests.csproj
│       │   ├── Controllers/
│       │   └── Services/
│       │
│       └── Gateway.Integration.Tests/ # Integration tests
│           ├── Gateway.Integration.Tests.csproj
│           └── ApiTests.cs
│
├── python-rag-api/                    # Python RAG API (App Service)
│   ├── README.md
│   ├── main.py                        # FastAPI entry point
│   ├── requirements.txt               # Python dependencies
│   ├── pytest.ini                     # Test configuration
│   ├── .env.example                   # Environment template
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py              # Route aggregator
│   │   │   │
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── health.py          # Health checks
│   │   │       ├── documents.py       # Document management
│   │   │       └── chat.py            # RAG queries
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Settings (Pydantic)
│   │   │   └── azure_clients.py       # Azure SDK clients
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py  # PDF/DOCX parsing
│   │   │   ├── embedding_service.py   # Azure OpenAI embeddings
│   │   │   ├── vector_store.py        # Azure AI Search
│   │   │   ├── rag_service.py         # RAG orchestration
│   │   │   ├── storage_service.py     # Blob + Cosmos
│   │   │   └── llm_service.py         # GPT-4 integration
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── document.py            # Document schemas
│   │   │   ├── chat.py                # Chat schemas
│   │   │   └── search.py              # Search schemas
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── file_utils.py          # File operations
│   │       ├── text_utils.py          # Text processing
│   │       └── azure_utils.py         # Azure helpers
│   │
│   └── tests/
│       ├── unit/
│       │   ├── test_document_processor.py
│       │   ├── test_embedding_service.py
│       │   ├── test_vector_store.py
│       │   └── test_rag_service.py
│       │
│       └── integration/
│           ├── test_document_upload.py
│           ├── test_chat_api.py
│           └── test_azure_services.py
│
├── infrastructure/                    # Infrastructure as Code
│   │
│   ├── bicep/                        # Azure Bicep templates
│   │   ├── main.bicep                # Main template
│   │   │
│   │   └── modules/
│   │       ├── storage.bicep         # Blob Storage
│   │       ├── openai.bicep          # Azure OpenAI
│   │       ├── search.bicep          # Azure AI Search
│   │       ├── cosmos.bicep          # Cosmos DB
│   │       ├── redis.bicep           # Azure Cache for Redis
│   │       ├── app-service-plan.bicep
│   │       ├── app-service.bicep
│   │       ├── static-web-app.bicep
│   │       ├── key-vault.bicep
│   │       └── app-insights.bicep
│   │
│   └── terraform/                    # Terraform (alternative)
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── modules/
│
├── docs/                             # Documentation
│   ├── architecture/
│   │   ├── DETAILED_ARCHITECTURE.md  # Comprehensive architecture
│   │   ├── DATA_FLOW.md              # Data flow diagrams
│   │   ├── SECURITY.md               # Security architecture
│   │   └── SCALABILITY.md            # Scaling strategy
│   │
│   ├── deployment/
│   │   ├── AZURE_SETUP.md            # Azure prerequisites
│   │   ├── LOCAL_DEV.md              # Local development
│   │   ├── CI_CD.md                  # CI/CD pipeline
│   │   └── COST_ESTIMATION.md        # Cost breakdown
│   │
│   └── api/
│       ├── GATEWAY_API.md            # .NET Gateway API docs
│       └── RAG_API.md                # Python RAG API docs
│
├── .github/
│   └── workflows/
│       ├── deploy-infrastructure.yml  # Deploy Azure resources
│       ├── deploy-frontend.yml        # Deploy React app
│       ├── deploy-gateway.yml         # Deploy .NET API
│       ├── deploy-python-api.yml      # Deploy Python API
│       └── run-tests.yml              # Run all tests
│
├── scripts/                          # Utility scripts
│   ├── setup-local.sh                # Local development setup
│   ├── deploy-azure.sh               # Azure deployment
│   ├── create-search-index.py        # Create AI Search index
│   └── seed-data.py                  # Seed test data
│
└── .gitignore                        # Git ignore rules
