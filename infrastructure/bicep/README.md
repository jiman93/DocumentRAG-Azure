# Infrastructure (Bicep)

This folder contains the Azure Resource Manager (ARM) templates written in **Bicep** that provision all cloud resources required for the Document RAG platform.

## Structure

- `main.bicep` – orchestrates module deployments and exposes consolidated outputs.
- `modules/` – reusable building blocks for individual services:
  - `storage.bicep` – Azure Storage account for blobs and other assets.
  - `openai.bicep` – Azure OpenAI resource for embeddings and chat completions.
  - `search.bicep` – Azure AI Search service (vector index backend).
  - `cosmos.bicep` – Cosmos DB account, SQL database, and containers.
  - `redis.bicep` – Optional Azure Cache for Redis for gateway caching.
  - `app-service-plan.bicep` – App Service plan hosting the Python API.
  - `app-service.bicep` – App Service (Web App) for the FastAPI backend.
  - `static-web-app.bicep` – Optional Static Web App for future UI.
  - `key-vault.bicep` – Key Vault for secrets and configuration.
  - `app-insights.bicep` – Application Insights for telemetry.

## Parameters

`main.bicep` exposes high-level knobs:

| Parameter              | Description                                         | Default    |
| ---------------------- | --------------------------------------------------- | ---------- |
| `resourcePrefix`     | Base prefix for resource names                      | `docrag` |
| `environment`        | Environment code (`dev`, `stg`, `prod`, etc.) | `dev`    |
| `location`           | Azure region                                        | `eastus` |
| `tenantId`           | AAD tenant ID (required for Key Vault)              | –         |
| `openAiLocation`     | Region for the Azure OpenAI resource                | same as `location` |
| `deploySearch`       | Whether to deploy Azure AI Search (vector store)    | `false`  |
| `deployRedis`        | Whether to deploy Redis cache                       | `false`  |
| `deployStaticWebApp` | Whether to deploy a Static Web App                  | `false`  |
| `deployBudget`       | Whether to create a Cost Management budget          | `false`  |
| `budgetAmount`       | Monthly budget amount in USD                        | `20`     |
| `budgetContactEmails`| Emails that receive budget alerts (required if `deployBudget=true`) | `[]` |
| `budgetStartDate`    | Budget start date (ISO 8601)                         | `utcNow()` |
| `budgetEndDate`      | Budget end date (ISO 8601)                           | `budgetStartDate + 1 year` |
| `tags`               | Additional resource tags                            | `{}`     |

## Deploying

```bash
# From repo root
cd infrastructure/bicep

# Validate template
az deployment group what-if \
  --resource-group document-rag \
  --template-file main.bicep \
  --parameters tenantId=dd70c224-0796-451b-b318-d298ed42c030 environment=dev location=southeastasia openAiLocation=eastus

# Deploy (resource-group scope)
az deployment group create \
  --resource-group document-rag \
  --template-file main.bicep \
  --parameters tenantId=dd70c224-0796-451b-b318-d298ed42c030 environment=dev location=southeastasia openAiLocation=eastus

# Include Azure AI Search (optional)
az deployment group create \
  --resource-group document-rag \
  --template-file main.bicep \
  --parameters tenantId=dd70c224-0796-451b-b318-d298ed42c030 environment=dev location=southeastasia openAiLocation=eastus deploySearch=true

# Add a $25 budget with email alerts
az deployment group create \
  --resource-group document-rag \
  --template-file main.bicep \
  --parameters tenantId=dd70c224-0796-451b-b318-d298ed42c030 environment=dev location=southeastasia openAiLocation=eastus deployBudget=true budgetAmount=25 budgetContactEmails='["you@example.com"]'
```

### Switching Vector Stores

- **Local development / zero cost:** keep `deploySearch=false` (default) and configure the API with `VECTOR_STORE_TYPE="chroma"`.
- **Azure AI Search:** set `deploySearch=true` during deployment and switch the API to `VECTOR_STORE_TYPE="azure_search"` with the endpoint/api key from outputs. To stop paying for Search, redeploy with `deploySearch=false` and delete the `docrag-*-search` resource.

> After toggling Azure Search off, the API will automatically fall back to the local Chroma database.
```

> Adjust scope/command (e.g. `group deployment`) if you prefer deploying into an existing resource group.

## Outputs

Deployment outputs include storage account name, OpenAI resource ID, Cosmos connection string, App Service URL, Key Vault URI, and optional Redis host—values you can feed directly into application configuration or CI/CD pipelines.
