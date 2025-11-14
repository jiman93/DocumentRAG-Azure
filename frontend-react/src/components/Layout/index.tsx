import { Link, useLocation, Outlet, useNavigate } from "react-router-dom";
import { FileText, MessageSquare, Upload, Menu, LogOut } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import ConversationList from "@/components/ConversationList";

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const navigation = [
    { name: "Upload", href: "/", icon: Upload },
    { name: "Documents", href: "/documents", icon: FileText },
    { name: "Chat", href: "/chat", icon: MessageSquare },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    logout();
    setSidebarOpen(false);
    navigate("/login", { replace: true });
  };

  return (
    <div className="h-screen flex overflow-hidden bg-gray-100">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
            <h1 className="text-xl font-bold text-gray-800">Document RAG</h1>
            <button className="lg:hidden" onClick={() => setSidebarOpen(false)}>
              <Menu className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto px-4 py-4">
            <nav className="space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                      ${
                        active
                          ? "bg-primary-50 text-primary-700"
                          : "text-gray-700 hover:bg-gray-100"
                      }
                    `}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>

            {location.pathname.startsWith("/chat") && (
              <ConversationList onSelect={() => setSidebarOpen(false)} />
            )}
          </div>

          {/* Logout */}
          <div className="px-4 pb-4 border-t border-gray-100">
            <button
              type="button"
              onClick={handleLogout}
              className="mt-4 w-full flex items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">Powered by Azure AI</p>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center px-4 lg:px-6">
          <button className="lg:hidden mr-4" onClick={() => setSidebarOpen(true)}>
            <Menu className="h-6 w-6" />
          </button>
          <h2 className="text-lg font-semibold text-gray-800">
            {navigation.find((item) => isActive(item.href))?.name || "Document RAG"}
          </h2>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
