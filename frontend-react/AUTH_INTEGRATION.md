# 🔐 Auth Integration Guide - Exact Changes Needed

## Files Created (3 new files)
1. ✅ `src/contexts/AuthContext.tsx` - Auth state management
2. ✅ `src/pages/LoginPage.tsx` - Login UI
3. ✅ `src/components/ProtectedRoute.tsx` - Route protection

---

## 📝 Changes Required

### 1. Update `src/App.tsx`

**Replace the entire file with:**

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import Layout from '@/components/Layout';
import HomePage from '@/pages/HomePage';
import DocumentsPage from '@/pages/DocumentsPage';
import ChatPage from '@/pages/ChatPage';
import LoginPage from '@/pages/LoginPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public route */}
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />} 
      />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout>
              <HomePage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/documents"
        element={
          <ProtectedRoute>
            <Layout>
              <DocumentsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <Layout>
              <ChatPage />
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

**What changed:**
- ✅ Added `AuthProvider` wrapper
- ✅ Added `/login` route
- ✅ Wrapped all existing routes in `ProtectedRoute`
- ✅ Added redirect logic (logged in users can't see login page)

---

### 2. Update `src/components/Layout/index.tsx`

**Add logout button to the sidebar footer. Replace the footer section (around line 65):**

```typescript
// FIND THIS (around line 65-70):
<div className="p-4 border-t border-gray-200">
  <p className="text-xs text-gray-500 text-center">
    Powered by Azure AI
  </p>
</div>

// REPLACE WITH THIS:
<div className="p-4 border-t border-gray-200 space-y-3">
  {/* User info */}
  <div className="flex items-center space-x-3 px-2">
    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
      <span className="text-sm font-semibold text-primary-700">
        {user?.name?.charAt(0).toUpperCase() || 'U'}
      </span>
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-sm font-medium text-gray-700 truncate">
        {user?.name || 'User'}
      </p>
      <p className="text-xs text-gray-500 truncate">
        {user?.email}
      </p>
    </div>
  </div>

  {/* Logout button */}
  <button
    onClick={logout}
    className="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
  >
    <LogOut className="mr-2 h-4 w-4" />
    Logout
  </button>

  <p className="text-xs text-gray-500 text-center pt-2 border-t">
    Powered by Azure AI
  </p>
</div>
```

**Add imports at the top:**

```typescript
// ADD these imports:
import { useAuth } from '@/contexts/AuthContext';
import { LogOut } from 'lucide-react';

// Your existing imports stay the same
```

**Add hook at the start of the component (after line 11):**

```typescript
export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  
  // ADD THIS LINE:
  const { user, logout } = useAuth();

  // ... rest of component
```

---

### 3. Update `src/services/api.ts` (Optional - for real auth)

**When you're ready to connect to real backend auth:**

Find the request interceptor (around line 17) and it's already there:

```typescript
// Already configured! Just make sure your backend returns a token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

**To connect to real login API, update `AuthContext.tsx` login function:**

```typescript
const login = async (email: string, password: string) => {
  try {
    // REPLACE the mock with real API call:
    const response = await api.post('/auth/login', { email, password });
    const { token, user } = response.data;
    
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    setUser(user);
  } catch (error) {
    console.error('Login failed:', error);
    throw new Error('Login failed');
  }
};
```

---

## 🎯 Summary of Changes

### Files Modified (2):
1. ✅ `src/App.tsx` - Add AuthProvider, login route, protect routes
2. ✅ `src/components/Layout/index.tsx` - Add user info & logout button

### Files Created (3):
1. ✅ `src/contexts/AuthContext.tsx` - Already created
2. ✅ `src/pages/LoginPage.tsx` - Already created
3. ✅ `src/components/ProtectedRoute.tsx` - Already created

---

## 🧪 How to Test

1. **Start the app:**
   ```bash
   npm run dev
   ```

2. **You'll be redirected to login** (not authenticated)

3. **Login with any credentials** (currently mocked)
   - Email: `test@example.com`
   - Password: `anything`

4. **After login:**
   - ✅ Redirected to home page
   - ✅ Can navigate between pages
   - ✅ See user info in sidebar
   - ✅ Logout button works

5. **After logout:**
   - ✅ Redirected to login page
   - ✅ Can't access protected routes

---

## 🔄 Current Auth Flow

```
User visits / → Not authenticated → Redirect to /login
                    ↓
User enters credentials → Mock login (accepts anything)
                    ↓
Token saved to localStorage → User state updated
                    ↓
Redirect to / → Can access all routes
                    ↓
Click Logout → Clear localStorage → Redirect to /login
```

---

## 🚀 Production Checklist

When ready for real auth:

- [ ] Update `AuthContext.tsx` login function to call real API
- [ ] Add registration page (optional)
- [ ] Add "Forgot Password" flow (optional)
- [ ] Add token refresh logic
- [ ] Handle 401 errors globally
- [ ] Add loading states during auth checks

---

## 💡 Quick Tips

**Demo credentials for now:**
- Any email/password combination works
- Perfect for showing the UI flow

**For real auth:**
- Your .NET Gateway should have `/auth/login` endpoint
- Return `{ token: string, user: { id, email, name } }`
- Frontend already sends token in all API requests

**Token in requests:**
- Already configured in `api.ts`
- Every API call automatically includes: `Authorization: Bearer <token>`

---

## 🎨 What It Looks Like

**Login Page:**
- Clean, centered form
- Email + password fields
- Loading state during login
- Error message display

**Sidebar Footer (after login):**
- User avatar with initial
- User name and email
- Logout button
- "Powered by Azure AI" text

---

That's it! Just 2 files to modify, and your auth is working! 🎉
