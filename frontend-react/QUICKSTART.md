# 🚀 React Frontend - Quick Start Guide

## Get Running in 5 Minutes

### 1. Install Dependencies
```bash
cd frontend-react-swa
npm install
```

### 2. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env - set your API URL
# For local dev with .NET Gateway:
echo "VITE_API_URL=http://localhost:7001/api/v1" > .env
```

### 3. Start Development Server
```bash
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

### 4. Test the UI

1. **Upload a Document**
   - Navigate to home page
   - Drag & drop a PDF or DOCX file
   - Watch upload progress

2. **View Documents**
   - Go to Documents page
   - See your uploaded files
   - Click a document to select it

3. **Chat with Document**
   - Go to Chat page
   - Ask questions about your document
   - See AI responses with sources

---

## Deploy to Azure Static Web Apps

### Prerequisites
- Azure subscription
- GitHub repository
- Backend API deployed

### Deployment Steps

#### Option 1: Azure Portal (Easiest)

1. **Go to Azure Portal**
   - Search for "Static Web Apps"
   - Click "Create"

2. **Configure**
   - Subscription: Your subscription
   - Resource Group: `rg-docrag-frontend`
   - Name: `docrag-frontend`
   - Region: `East US 2`
   - Source: `GitHub`
   - Connect your repository
   - Branch: `main`
   - Build Presets: `React`
   - App location: `/frontend-react-swa`
   - Output location: `dist`

3. **Add Environment Variable**
   - After creation, go to Configuration
   - Add: `VITE_API_URL` = `https://your-gateway.azurewebsites.net/api/v1`

4. **Deploy**
   - Push to main branch
   - GitHub Actions will auto-deploy

#### Option 2: Azure CLI (Faster)

```bash
# Login
az login

# Create Static Web App
az staticwebapp create \
  --name docrag-frontend \
  --resource-group rg-docrag \
  --source https://github.com/YOUR_USERNAME/YOUR_REPO \
  --location eastus2 \
  --branch main \
  --app-location "/frontend-react-swa" \
  --output-location "dist" \
  --login-with-github

# Configure environment
az staticwebapp appsettings set \
  --name docrag-frontend \
  --setting-names VITE_API_URL=https://your-gateway.azurewebsites.net/api/v1
```

#### Option 3: Manual Build & Deploy

```bash
# Build locally
npm run build

# Install SWA CLI
npm install -g @azure/static-web-apps-cli

# Deploy
swa deploy ./dist \
  --app-name docrag-frontend \
  --resource-group rg-docrag \
  --env production
```

---

## Project Structure at a Glance

```
frontend-react-swa/
├── src/
│   ├── components/         # UI components
│   │   ├── ChatInterface/  # Chat UI
│   │   ├── DocumentUpload/ # Upload UI
│   │   └── Layout/         # App shell
│   ├── pages/              # Page routes
│   │   ├── HomePage.tsx    # Upload page
│   │   ├── DocumentsPage.tsx
│   │   └── ChatPage.tsx
│   ├── services/api.ts     # API client
│   ├── hooks/useApi.ts     # React Query hooks
│   ├── store/index.ts      # Zustand stores
│   └── types/index.ts      # TypeScript types
├── staticwebapp.config.json # Azure SWA config
└── package.json
```

---

## Common Issues & Solutions

### Issue: API calls failing with CORS error
**Solution**: 
- Check `VITE_API_URL` in `.env`
- Ensure .NET Gateway has CORS configured:
  ```json
  "Cors": {
    "AllowedOrigins": ["http://localhost:3000"]
  }
  ```

### Issue: Build fails with TypeScript errors
**Solution**:
```bash
# Check for type errors
npm run build

# If needed, update types
npm install -D @types/react@latest @types/react-dom@latest
```

### Issue: Environment variables not working in production
**Solution**:
- Azure SWA: Set in Portal → Configuration
- Variables must start with `VITE_`
- Restart the app after changing

### Issue: Page not found (404) on refresh
**Solution**: Already configured in `staticwebapp.config.json`
```json
{
  "navigationFallback": {
    "rewrite": "/index.html"
  }
}
```

---

## Development Tips

### Hot Reload
- Changes auto-reflect in browser
- No manual refresh needed

### API Proxy (Local Dev)
```typescript
// vite.config.ts already configured
server: {
  proxy: {
    '/api': 'http://localhost:7001'
  }
}
```

### State Persistence
- Chat and documents saved to localStorage
- Survives page refresh
- Clear with: `localStorage.clear()`

### Build Optimization
```bash
# Analyze bundle size
npm run build
ls -lh dist/assets/*.js
```

---

## Tech Stack Quick Reference

| Purpose | Library |
|---------|---------|
| UI Framework | React 18 |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| State | Zustand |
| Data Fetching | TanStack Query |
| HTTP Client | Axios |
| Routing | React Router |
| Icons | Lucide React |
| File Upload | React Dropzone |
| Markdown | React Markdown |

---

## Next Steps

1. ✅ Get it running locally
2. ✅ Test all features (upload, chat, documents)
3. ✅ Deploy to Azure Static Web Apps
4. 🎨 Customize colors in `tailwind.config.js`
5. 🔐 Add authentication if needed
6. 📊 Add analytics tracking

---

## Need Help?

- **Frontend Issues**: Check browser console (F12)
- **API Issues**: Check Network tab in DevTools
- **Build Issues**: Read full error in terminal

**Documentation**: See [README.md](./README.md) for detailed info

---

**You're all set! 🎉**

Your React frontend is ready for Azure Static Web Apps integration!
