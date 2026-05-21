import { Outlet, Link } from 'react-router-dom';
import { Activity, Shield, LayoutDashboard, Database, Settings } from 'lucide-react';

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-50 text-gray-900">
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="flex items-center justify-center h-16 border-b border-gray-200">
          <Shield className="w-8 h-8 text-blue-600 mr-2" />
          <span className="text-xl font-bold">FairLens AI</span>
        </div>
        <nav className="p-4 space-y-1">
          <Link to="/" className="flex items-center px-4 py-2 text-gray-700 bg-gray-100 rounded-md">
            <LayoutDashboard className="w-5 h-5 mr-3" />
            Dashboard
          </Link>
          <Link to="/datasets" className="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-md">
            <Database className="w-5 h-5 mr-3" />
            Datasets
          </Link>
          <Link to="/models" className="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-md">
            <Activity className="w-5 h-5 mr-3" />
            Models
          </Link>
          <Link to="/settings" className="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-md">
            <Settings className="w-5 h-5 mr-3" />
            Settings
          </Link>
        </nav>
      </aside>
      
      <main className="flex-1 overflow-auto">
        <header className="flex items-center justify-between h-16 px-6 bg-white border-b border-gray-200">
          <h1 className="text-xl font-semibold">Overview</h1>
          <div className="flex items-center space-x-4">
            <button className="text-sm font-medium text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </header>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
