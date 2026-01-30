import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import type { UserRole } from '@/types'

interface RoleGuardProps {
  allowedRoles: UserRole[]
}

export function RoleGuard({ allowedRoles }: RoleGuardProps) {
  const profile = useAuthStore((s) => s.profile)

  if (!profile || !allowedRoles.includes(profile.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
