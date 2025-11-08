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

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resourcePrefix` | Base prefix for resource names | `docrag` |
| `environment` | Environment code (`dev`, `stg`, `prod`, etc.) | `dev` |
| `location` | Azure region | `eastus` |
| `tenantId` | AAD tenant ID (required for Key Vault) | – |
| `deployRedis` | Whether to deploy Redis cache | `false` |
| `deployStaticWebApp` | Whether to deploy a Static Web App | `false` |
| `tags` | Additional resource tags | `{}` |

## Deploying

```bash
# From repo root
cd infrastructure/bicep

# Validate template
az deployment sub what-if \
  --location eastus \
  --template-file main.bicep \
  --parameters tenantId=<tenant-guid> environment=dev

# Deploy (subscription-level)
az deployment sub create \
  --location eastus \
  --template-file main.bicep \
  --parameters tenantId=<tenant-guid> environment=dev
```

> Adjust scope/command (e.g. `group deployment`) if you prefer deploying into an existing resource group.

## Outputs

Deployment outputs include storage account name, OpenAI resource ID, Cosmos connection string, App Service URL, Key Vault URI, and optional Redis host—values you can feed directly into application configuration or CI/CD pipelines.

