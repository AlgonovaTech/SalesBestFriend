import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { useUIStore } from '@/stores/uiStore'
import { cn } from '@/lib/utils'

export function AppLayout() {
  const sidebarOpen = useUIStore((s) => s.sidebarOpen)

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <main
        className={cn(
          'min-h-screen transition-all duration-200',
          sidebarOpen ? 'ml-60' : 'ml-16'
        )}
      >
        <div className="mx-auto max-w-[1400px] p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
