import { Link } from 'react-router-dom'
import { useOverviewStats } from '@/hooks/useAnalytics'
import { useCalls } from '@/hooks/useCalls'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Phone, BarChart3, ListChecks, TrendingUp, Mic } from 'lucide-react'
import { formatDate, formatDuration } from '@/lib/utils'

export function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useOverviewStats()
  const { data: recentCalls, isLoading: callsLoading } = useCalls({ per_page: 5 })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Overview of your sales performance.
          </p>
        </div>
        <Link to="/live">
          <Button>
            <Mic className="mr-2 h-4 w-4" />
            Start Call
          </Button>
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Calls"
          value={stats?.total_calls}
          icon={Phone}
          loading={statsLoading}
        />
        <StatCard
          title="This Week"
          value={stats?.calls_this_week}
          icon={TrendingUp}
          loading={statsLoading}
        />
        <StatCard
          title="Avg. Score"
          value={stats?.average_score != null ? `${stats.average_score}` : undefined}
          icon={BarChart3}
          loading={statsLoading}
        />
        <StatCard
          title="Pending Tasks"
          value={stats?.total_tasks_pending}
          icon={ListChecks}
          loading={statsLoading}
        />
      </div>

      {/* Recent Calls */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <CardTitle className="text-base">Recent Calls</CardTitle>
          <Link to="/calls">
            <Button variant="ghost" size="sm" className="text-xs">
              View All
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {callsLoading &&
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex items-center justify-between">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-4 w-24" />
                </div>
              ))}

            {recentCalls?.data.map((call) => (
              <Link
                key={call.id}
                to={`/calls/${call.id}`}
                className="flex items-center justify-between rounded-md px-2 py-2 transition-colors hover:bg-muted"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{call.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDate(call.created_at)}
                    {call.duration_seconds
                      ? ` · ${formatDuration(call.duration_seconds)}`
                      : ''}
                  </p>
                </div>
                <Badge variant="secondary" className="ml-3 text-xs">
                  {call.status}
                </Badge>
              </Link>
            ))}

            {!callsLoading && recentCalls?.data.length === 0 && (
              <p className="py-6 text-center text-sm text-muted-foreground">
                No calls yet. Start your first call to see data here.
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon: Icon,
  loading,
}: {
  title: string
  value: string | number | undefined
  icon: typeof Phone
  loading: boolean
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 pt-6">
        <div className="rounded-md bg-muted p-2.5">
          <Icon className="h-5 w-5 text-muted-foreground" />
        </div>
        <div>
          {loading ? (
            <Skeleton className="h-7 w-16" />
          ) : (
            <p className="text-2xl font-bold">{value ?? 0}</p>
          )}
          <p className="text-xs text-muted-foreground">{title}</p>
        </div>
      </CardContent>
    </Card>
  )
}
