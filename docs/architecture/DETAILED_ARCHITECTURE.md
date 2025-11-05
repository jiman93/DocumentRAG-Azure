# Document RAG - Azure Architecture Documentation

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                         USER LAYER                                │
│                                                                   │
│    ┌─────────────────────────────────────────────────────┐      │
│    │         Web Browser / Mobile App                     │      │
│    └──────────────────────┬──────────────────────────────┘      │
└───────────────────────────┼──────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                           │
│                                                                   │
│    ┌─────────────────────────────────────────────────────┐      │
│    │          React SPA (TypeScript)                     │      │
│    │          Azure Static Web Apps                      │      │
│    │                                                     │      │
│    │  Features:                                          │      │
│    │  • Document Upload Interface                        │      │
│    │  • Real-time Chat UI                               │      │
│    │  • Source Citation Display                          │      │
│    │  • Conversation History                             │      │
│    │  • Responsive Design                                │      │
│    └──────────────────────┬──────────────────────────────┘      │
└───────────────────────────┼──────────────────────────────────────┘
                            │ HTTPS/REST
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                     API GATEWAY LAYER                             │
│                                                                   │
│    ┌─────────────────────────────────────────────────────┐      │
│    │       .NET Gateway (ASP.NET Core 8)                 │      │
│    │       Azure App Service (Windows/Linux)             │      │
│    │                                                     │      │
│    │  Responsibilities:                                  │      │
│    │  ✓ Authentication & Authorization                   │      │
│    │    - JWT Token Validation                           │      │
│    │    - Azure AD B2C Integration                       │      │
│    │    - Role-Based Access Control (RBAC)              │      │
│    │                                                     │      │
│    │  ✓ Caching Layer (Redis)                           │      │
│    │    - Response Caching (30min TTL)                  │      │
│    │    - Query Results Caching                         │      │
│    │    - Session State                                 │      │
│    │                                                     │      │
│    │  ✓ Rate Limiting & Throttling                      │      │
│    │    - IP-based limits (100 req/min)                 │      │
│    │    - User-based limits (1000 req/hour)             │      │
│    │    - Token bucket algorithm                        │      │
│    │                                                     │      │
│    │  ✓ Request/Response Transformation                 │      │
│    │    - Input Validation (FluentValidation)           │      │
│    │    - DTO Mapping                                   │      │
│    │    - Error Normalization                           │      │
│    │                                                     │      │
│    │  ✓ Monitoring & Logging                            │      │
│    │    - Structured Logging (Serilog)                  │      │
│    │    - Distributed Tracing                           │      │
│    │    - Performance Metrics                           │      │
│    │                                                     │      │
│    │  ✓ Resilience Patterns (Polly)                     │      │
│    │    - Retry with exponential backoff                │      │
│    │    - Circuit breaker                               │      │
│    │    - Timeout policies                              │      │
│    └──────────────────────┬──────────────────────────────┘      │
└───────────────────────────┼──────────────────────────────────────┘
                            │ Internal HTTP
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                    RAG PROCESSING LAYER                           │
│                                                                   │
│    ┌─────────────────────────────────────────────────────┐      │
│    │    Python RAG API (FastAPI + LangChain)             │      │
│    │    Azure App Service (Linux, Python 3.11)           │      │
│    │                                                     │      │
│    │  Core Services:                                     │      │
│    │                                                     │      │
│    │  1️⃣ Document Processing Pipeline                   │      │
│    │     • File Upload Handler                           │      │
│    │     • Format Detection (PDF/DOCX/TXT)              │      │
│    │     • Text Extraction                               │      │
│    │     • Metadata Extraction                           │      │
│    │                                                     │      │
│    │  2️⃣ Chunking Engine                                │      │
│    │     • RecursiveCharacterTextSplitter               │      │
│    │     • Semantic chunking (1000 chars)               │      │
│    │     • 200 char overlap for context                 │      │
│    │     • Preserve sentence boundaries                 │      │
│    │                                                     │      │
│    │  3️⃣ Embedding Service                              │      │
│    │     • Azure OpenAI text-embedding-ada-002          │      │
│    │     • Batch processing (100 chunks/batch)          │      │
│    │     • Embedding cache (Redis)                      │      │
│    │     • 1536-dimension vectors                       │      │
│    │                                                     │      │
│    │  4️⃣ Vector Store Operations                        │      │
│    │     • Azure AI Search integration                  │      │
│    │     • Hybrid search (vector + keyword)             │      │
│    │     • Metadata filtering                           │      │
│    │     • Relevance scoring                            │      │
│    │                                                     │      │
│    │  5️⃣ RAG Orchestration                              │      │
│    │     • Query understanding                          │      │
│    │     • Context retrieval (top-5)                    │      │
│    │     • Prompt engineering                           │      │
│    │     • LLM generation (GPT-4)                       │      │
│    │     • Source attribution                           │      │
│    │     • Response streaming                           │      │
│    │                                                     │      │
│    │  6️⃣ Conversation Management                        │      │
│    │     • History tracking                             │      │
│    │     • Context window management                    │      │
│    │     • Multi-turn conversations                     │      │
│    └──────────────────────┬──────────────────────────────┘      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                    AZURE SERVICES LAYER                           │
│                                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │ Azure OpenAI  │  │ Azure AI      │  │ Blob Storage  │       │
│  │               │  │ Search        │  │               │       │
│  │ • GPT-4       │  │ • Vector DB   │  │ • Documents   │       │
│  │ • Embeddings  │  │ • Hybrid      │  │ • Raw files   │       │
│  │ • 10K TPM     │  │   Search      │  │ • Hot tier    │       │
│  │ • Streaming   │  │ • Semantic    │  │               │       │
│  └───────────────┘  │   Ranking     │  └───────────────┘       │
│                     │ • Filters     │                           │
│                     └───────────────┘                           │
│                                                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │ Cosmos DB     │  │ Redis Cache   │  │ Key Vault     │       │
│  │               │  │               │  │               │       │
│  │ • Metadata    │  │ • Sessions    │  │ • API Keys    │       │
│  │ • Conversations│  │ • Embeddings │  │ • Secrets     │       │
│  │ • User data   │  │ • Results     │  │ • Certificates│       │
│  │ • NoSQL       │  │ • 30min TTL   │  │ • Managed ID  │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │         Application Insights + Log Analytics       │         │
│  │         • Distributed tracing                      │         │
│  │         • Custom metrics                           │         │
│  │         • Real-time monitoring                     │         │
│  └────────────────────────────────────────────────────┘         │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Document Upload Flow

```
User → React SPA → .NET Gateway → Python API
                                      ↓
                            Extract Text (pypdf/docx)
                                      ↓
                            Chunk Text (1000/200 overlap)
                                      ↓
                            Generate Embeddings (OpenAI)
                                      ↓
                         Store in AI Search + Blob + Cosmos
```

### 2. Query Flow

```
User Question → React SPA → .NET Gateway (Auth+Cache) → Python API
                                                            ↓
                                                   Generate Query Embedding
                                                            ↓
                                              Vector Search (Azure AI Search)
                                                            ↓
                                                  Retrieve Top-5 Chunks
                                                            ↓
                                                    Build Context Prompt
                                                            ↓
                                                Generate Answer (GPT-4)
                                                            ↓
                                        Stream Response ← Cache ← Gateway ← User
```

## Technology Justification

### Why .NET Gateway?

1. **Enterprise Credibility** : Shows .NET expertise for Access Group role
2. **Performance** : Faster than pure Python for proxy/caching operations
3. **Azure Native** : Best integration with Azure services (AD, Key Vault)
4. **Caching** : Superior Redis integration with StackExchange.Redis
5. **Security** : Robust auth/authz libraries

### Why Python RAG API?

1. **AI/ML Ecosystem** : LangChain, transformers, pandas
2. **Rapid Development** : Faster to iterate on RAG logic
3. **Community** : Better AI/ML libraries and examples
4. **Your Strength** : Demonstrates your core AI expertise

### Why This Split?

* **Separation of Concerns** : Gateway handles infrastructure, Python handles AI
* **Independent Scaling** : Scale each layer independently
* **Best Tool for Job** : Use strengths of each platform
* **Career Showcase** : Demonstrates full-stack + AI capabilities

## Security Architecture

### Authentication Flow

```
User Login → Azure AD B2C → JWT Token → .NET Gateway validates → 
Sets claims → Forwards to Python API (with user context)
```

### Secrets Management

* All secrets in Azure Key Vault
* Managed Identity for service-to-service auth
* No hardcoded credentials
* Automatic secret rotation

## Scalability

### Horizontal Scaling

* Frontend: CDN + global distribution (Azure Static Web Apps)
* Gateway: Auto-scale based on CPU/memory (App Service)
* Python API: Auto-scale based on request count
* Vector DB: Azure AI Search scales automatically
* Cache: Redis cluster for high availability

### Performance Targets

* P95 Latency: <2s for queries
* Document Processing: <30s for 10MB PDFs
* Cache Hit Rate: >70%
* Concurrent Users: 1000+
* TPM: 10,000+ (OpenAI limit)

## Cost Estimation

### Development Environment (~$100/month)

* Static Web Apps: Free
* App Service (B1): $13/month × 2 = $26
* Azure OpenAI (Pay-as-you-go): ~$30
* AI Search (Basic): $75/month
* Redis (Basic C0): $16/month
* Cosmos DB (Serverless): ~$5
* Blob Storage: ~$5

### Production Environment (~$500/month)

* Static Web Apps (Standard): $9/month
* App Service (P1V2): $117/month × 2 = $234
* Azure OpenAI: ~$150 (10K req/day)
* AI Search (Standard): $250/month
* Redis (Standard C1): $55/month
* Cosmos DB: ~$50
* Application Insights: ~$50

## Monitoring Strategy

### Application Insights Dashboards

1. **User Experience** : Page load times, user flows
2. **API Performance** : Response times, error rates
3. **RAG Metrics** : Embedding generation, vector search latency
4. **Cost Tracking** : OpenAI token usage, search queries

### Alerts

* Response time > 5s
* Error rate > 5%
* OpenAI quota exceeded
* Search service degraded

## Deployment Strategy

### CI/CD Pipeline (GitHub Actions)

```
git push → Tests → Build → Deploy to Dev → 
Integration Tests → Deploy to Staging → 
Manual Approval → Deploy to Production
```

### Blue-Green Deployment

* Deploy to staging slot
* Run smoke tests
* Swap slots (zero downtime)
* Monitor for 1 hour
* Rollback if issues

## Disaster Recovery

* **RTO** : 1 hour (Recovery Time Objective)
* **RPO** : 5 minutes (Recovery Point Objective)
* **Backup** : Cosmos DB continuous backup
* **Geo-redundancy** : Azure AI Search geo-replicated
* **Failover** : Automatic for most Azure services

## Future Enhancements

1. **Multi-modal RAG** : Support images, videos
2. **Advanced Chunking** : Semantic chunking with ML
3. **Fine-tuning** : Custom models for domain
4. **Federated Search** : Query multiple knowledge bases
5. **Conversation Memory** : Long-term user context
6. **Real-time Updates** : WebSocket streaming
7. **Mobile Apps** : Native iOS/Android

## References

* [Azure Architecture Center - RAG](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/rag-solution)
* [LangChain Azure Integration](https://python.langchain.com/docs/integrations/platforms/microsoft)
* [Azure OpenAI Best Practices](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/best-practices)
