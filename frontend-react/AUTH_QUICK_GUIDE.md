# 🔐 Auth Integration - Quick Guide

## ✅ Files Already Created

1. `src/contexts/AuthContext.tsx` - Auth logic
2. `src/pages/LoginPage.tsx` - Login UI  
3. `src/components/ProtectedRoute.tsx` - Route guard

## 📝 What You Need to Change

### 1. `src/App.tsx` - Wrap everything in auth

```typescript
// Add imports:
import { AuthProvider } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import LoginPage from '@/pages/LoginPage';

// Wrap QueryClientProvider with AuthProvider
// Add /login route
// Wrap existing routes in <ProtectedRoute>
```

**See full code in:** [AUTH_INTEGRATION.md](computer:///mnt/user-data/outputs/frontend-react-swa/AUTH_INTEGRATION.md) (Section 1)

---

### 2. `src/components/Layout/index.tsx` - Add logout

```typescript
// Add imports:
import { useAuth } from '@/contexts/AuthContext';
import { LogOut } from 'lucide-react';

// Add hook:
const { user, logout } = useAuth();

// Replace footer section with user info + logout button
```

**See full code in:** [AUTH_INTEGRATION.md](computer:///mnt/user-data/outputs/frontend-react-swa/AUTH_INTEGRATION.md) (Section 2)

---

## 🎯 That's It!

**Only 2 files to modify:**
1. ✅ `App.tsx` - 30 lines
2. ✅ `Layout/index.tsx` - 20 lines

**Result:**
- 🔒 All routes protected
- 🔑 Login page
- 👤 User info in sidebar
- 🚪 Logout button
- 💾 Session persistence

---

## 🧪 Test It

```bash
npm run dev
```

1. Visit app → Redirected to login
2. Enter any email/password → Logged in
3. Navigate pages → Works
4. Click Logout → Back to login
5. Refresh page → Still logged in (localStorage)

---

## 📖 Full Documentation

**[Read AUTH_INTEGRATION.md](computer:///mnt/user-data/outputs/frontend-react-swa/AUTH_INTEGRATION.md)** for:
- Complete code snippets
- Production setup
- Real API integration
- Testing guide

---

**Current status:** Mock auth (accepts any credentials)  
**For production:** Update `AuthContext.tsx` to call your .NET Gateway auth endpoint
