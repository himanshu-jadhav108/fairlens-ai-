import { useState, type ReactNode } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";
import MobileBottomNav from "./MobileBottomNav";
import ColdStartOnboarding from "./ColdStartOnboarding";

export default function AppLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      <ColdStartOnboarding />
      <div className="min-h-screen bg-background grid-bg">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div className="md:ml-60">
          <Header onMenuClick={() => setSidebarOpen(true)} />
          <main className="px-3 py-4 md:p-6 pb-20 md:pb-6">{children}</main>
        </div>
        <MobileBottomNav />
      </div>
    </>
  );
}
