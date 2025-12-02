# 🚀 Local Development Guide

## Quick Start - Run All 3 Services

### Prerequisites
- **Python 3.11+** with `pip`
- **.NET 9 SDK** (or .NET 8)
- **Node.js 20+** with `npm`

---

## Step-by-Step Setup

### 1️⃣ Python RAG API (Port 8000)

```bash
cd python-rag-api

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Create .env file (if it doesn't exist)
cat > .env << EOF
# Required: OpenAI API Key (choose one)
OPENAI_API_KEY=sk-your-openai-key-here

# OR use Azure OpenAI
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_KEY=your-azure-key
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
# AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
# AZURE_OPENAI_API_VERSION=2024-02-01

# Optional: Azure services (will use local fallbacks if not set)
# AZURE_STORAGE_CONNECTION_STRING=...
# AZURE_COSMOS_ENDPOINT=...
# AZURE_COSMOS_KEY=...
EOF

# Run the API
python main.py
```

**✅ Verify**: Open http://localhost:8000/docs

---

### 2️⃣ .NET Gateway (Port 7001)

Open a **new terminal**:

```bash
cd dotnet-gateway

# Restore packages (first time only)
dotnet restore

# Run the gateway
cd src/Gateway.Api
dotnet run
```

**✅ Verify**: Open https://localhost:7001/swagger

**Note**: The gateway is already configured to point to `http://localhost:8000` for the Python API.

---

### 3️⃣ React Frontend (Port 3000)

Open a **new terminal**:

```bash
cd frontend-react

# Install dependencies (first time only)
npm install

# Create .env file (optional - defaults to localhost:7001)
echo "VITE_API_URL=http://localhost:7001/api/v1" > .env

# Run the frontend
npm run dev
```

**✅ Verify**: Open http://localhost:3000 (or the port shown in terminal)

---

## 🎯 All Services Running

| Service | URL | Status Check |
|---------|-----|--------------|
| **Python RAG API** | http://localhost:8000 | http://localhost:8000/health |
| **.NET Gateway** | https://localhost:7001 | https://localhost:7001/health |
| **React Frontend** | http://localhost:3000 | http://localhost:3000 |

---

## 🔧 Troubleshooting

### Python API won't start
- **Check**: Is port 8000 already in use?
  ```bash
  lsof -i :8000  # macOS/Linux
  netstat -ano | findstr :8000  # Windows
  ```
- **Fix**: Kill the process or change port in `main.py`

### .NET Gateway won't start
- **Check**: Is port 7001 already in use?
- **Fix**: Check `launchSettings.json` or kill the process

### Frontend can't connect to Gateway
- **Check**: Is the gateway running on port 7001?
- **Check**: Is `VITE_API_URL` set correctly in `.env`?
- **Fix**: Restart the frontend after changing `.env`

### Gateway can't connect to Python API
- **Check**: Is Python API running on port 8000?
- **Check**: `appsettings.json` has `PythonRagApiUrl: "http://localhost:8000"`

### OpenAI API errors
- **Check**: Is your API key valid?
- **Check**: Do you have credits/quota?
- **Test**: Try calling OpenAI API directly

---

## 📝 Environment Variables Reference

### Python RAG API (.env)
```bash
# Required - Choose one:
OPENAI_API_KEY=sk-...                    # Standard OpenAI
# OR
AZURE_OPENAI_ENDPOINT=https://...        # Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Optional - Local fallbacks available:
AZURE_STORAGE_CONNECTION_STRING=...      # Falls back to local files
AZURE_COSMOS_ENDPOINT=...                # Falls back to SQLite
AZURE_COSMOS_KEY=...
```

### .NET Gateway (appsettings.json)
- Already configured for local development
- No changes needed unless you want to use Redis

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:7001/api/v1
```

---

## 🚀 Quick Commands

### Run all services in separate terminals:
```bash
# Terminal 1: Python API
cd python-rag-api && source venv/bin/activate && python main.py

# Terminal 2: .NET Gateway
cd dotnet-gateway/src/Gateway.Api && dotnet run

# Terminal 3: Frontend
cd frontend-react && npm run dev
```

### Or use a process manager (optional):
```bash
# Install concurrently
npm install -g concurrently

# Run all at once
concurrently \
  "cd python-rag-api && source venv/bin/activate && python main.py" \
  "cd dotnet-gateway/src/Gateway.Api && dotnet run" \
  "cd frontend-react && npm run dev"
```

---

## ✅ Verification Checklist

- [ ] Python API responds at http://localhost:8000/health
- [ ] Python API docs available at http://localhost:8000/docs
- [ ] .NET Gateway responds at https://localhost:7001/health
- [ ] .NET Gateway Swagger at https://localhost:7001/swagger
- [ ] Frontend loads at http://localhost:3000
- [ ] Frontend can call Gateway API (check browser console)
- [ ] Gateway can call Python API (check gateway logs)

---

## 🎉 You're Ready!

Once all services are running, you can:
1. Upload documents via the frontend
2. Ask questions about your documents
3. View API docs at `/swagger` and `/docs` endpoints
4. Check health endpoints for monitoring

**Happy coding! 🚀**

