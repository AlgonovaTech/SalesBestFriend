import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'
import {
  LayoutDashboard,
  Phone,
  Mic,
  BookOpen,
  BarChart3,
  Settings,
  LogOut,
  ChevronLeft,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useAuth } from '@/hooks/useAuth'

interface NavItem {
  to: string
  label: string
  icon: typeof LayoutDashboard
  roles?: string[]
}

const navItems: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/calls', label: 'Calls', icon: Phone },
  { to: '/live', label: 'Live Call', icon: Mic },
  { to: '/playbooks', label: 'Playbooks', icon: BookOpen, roles: ['admin', 'team_lead'] },
  { to: '/analytics', label: 'Analytics', icon: BarChart3, roles: ['admin', 'team_lead'] },
]

export function Sidebar() {
  const profile = useAuthStore((s) => s.profile)
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { signOut } = useAuth()

  const initials = profile?.full_name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) ?? '?'

  return (
    <aside
      className={cn(
        'fixed inset-y-0 left-0 z-30 flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-200',
        sidebarOpen ? 'w-60' : 'w-16'
      )}
    >
      {/* Header */}
      <div className="flex h-14 items-center justify-between px-4">
        {sidebarOpen && (
          <span className="text-sm font-semibold tracking-tight">
            Sales Best Friend
          </span>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-sidebar-foreground hover:bg-sidebar-accent"
          onClick={toggleSidebar}
        >
          <ChevronLeft
            className={cn(
              'h-4 w-4 transition-transform',
              !sidebarOpen && 'rotate-180'
            )}
          />
        </Button>
      </div>

      <Separator className="bg-sidebar-border" />

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-2 py-3">
        {navItems.map((item) => {
          if (item.roles && profile && !item.roles.includes(profile.role)) {
            return null
          }
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
                )
              }
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          )
        })}
      </nav>

      <Separator className="bg-sidebar-border" />

      {/* Footer */}
      <div className="p-2">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              isActive
                ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
            )
          }
        >
          <Settings className="h-4 w-4 shrink-0" />
          {sidebarOpen && <span>Settings</span>}
        </NavLink>

        <div className="mt-2 flex items-center gap-3 rounded-md px-3 py-2">
          <Avatar className="h-7 w-7">
            <AvatarFallback className="bg-sidebar-primary text-xs text-sidebar-primary-foreground">
              {initials}
            </AvatarFallback>
          </Avatar>
          {sidebarOpen && (
            <div className="flex flex-1 items-center justify-between">
              <div className="min-w-0">
                <p className="truncate text-xs font-medium">{profile?.full_name}</p>
                <p className="truncate text-[10px] text-sidebar-foreground/50">
                  {profile?.role?.replace('_', ' ')}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-sidebar-foreground/50 hover:bg-sidebar-accent hover:text-sidebar-foreground"
                onClick={signOut}
              >
                <LogOut className="h-3.5 w-3.5" />
              </Button>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
