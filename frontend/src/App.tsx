import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from '@/components/ui/sonner'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { RoleGuard } from '@/components/auth/RoleGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { ErrorBoundary } from '@/components/layout/ErrorBoundary'
import { Skeleton } from '@/components/ui/skeleton'

// Lazy-loaded pages
const LoginPage = lazy(() => import('@/pages/auth/LoginPage').then(m => ({ default: m.LoginPage })))
const RegisterPage = lazy(() => import('@/pages/auth/RegisterPage').then(m => ({ default: m.RegisterPage })))
const DashboardPage = lazy(() => import('@/pages/dashboard/DashboardPage').then(m => ({ default: m.DashboardPage })))
const CallsListPage = lazy(() => import('@/pages/calls/CallsListPage').then(m => ({ default: m.CallsListPage })))
const CallDetailPage = lazy(() => import('@/pages/calls/CallDetailPage').then(m => ({ default: m.CallDetailPage })))
const LiveCallPage = lazy(() => import('@/pages/live/LiveCallPage').then(m => ({ default: m.LiveCallPage })))
const PlaybookListPage = lazy(() => import('@/pages/playbook/PlaybookListPage').then(m => ({ default: m.PlaybookListPage })))
const PlaybookEditorPage = lazy(() => import('@/pages/playbook/PlaybookEditorPage').then(m => ({ default: m.PlaybookEditorPage })))
const TeamAnalyticsPage = lazy(() => import('@/pages/analytics/TeamAnalyticsPage').then(m => ({ default: m.TeamAnalyticsPage })))
const SettingsPage = lazy(() => import('@/pages/settings/SettingsPage').then(m => ({ default: m.SettingsPage })))

function PageLoader() {
  return (
    <div className="space-y-4 p-6">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-[300px]" />
    </div>
  )
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Authenticated routes */}
            <Route element={<AuthGuard />}>
              <Route element={<AppLayout />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/calls" element={<CallsListPage />} />
                <Route path="/calls/:id" element={<CallDetailPage />} />
                <Route path="/live" element={<LiveCallPage />} />
                <Route path="/settings" element={<SettingsPage />} />

                {/* Admin/Lead only */}
                <Route element={<RoleGuard allowedRoles={['admin', 'team_lead']} />}>
                  <Route path="/playbooks" element={<PlaybookListPage />} />
                  <Route path="/playbooks/:id" element={<PlaybookEditorPage />} />
                  <Route path="/analytics" element={<TeamAnalyticsPage />} />
                </Route>
              </Route>
            </Route>

            {/* Redirect root */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
      <Toaster position="bottom-right" />
      </ErrorBoundary>
    </QueryClientProvider>
  )
}
