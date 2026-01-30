import { useMemo } from 'react'
import { useScheduledCalls } from '@/hooks/useScheduledCalls'
import { ScheduledCallCard } from '@/components/scheduled/ScheduledCallCard'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Calendar, CalendarDays } from 'lucide-react'
import type { Call } from '@/types'

export function ScheduledCallsPage() {
  const { data: scheduled, isLoading } = useScheduledCalls()

  // Group calls by date
  const grouped = useMemo(() => {
    if (!scheduled?.data) return { today: [], upcoming: [] }

    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)

    const todayCalls: Call[] = []
    const upcomingCalls: Call[] = []

    for (const call of scheduled.data) {
      const scheduledAt = call.pre_call_data?.scheduled_at || call.started_at
      if (!scheduledAt) {
        upcomingCalls.push(call)
        continue
      }

      const date = new Date(scheduledAt)
      if (date >= today && date < tomorrow) {
        todayCalls.push(call)
      } else {
        upcomingCalls.push(call)
      }
    }

    // Sort by time
    const sortByTime = (a: Call, b: Call) => {
      const at = a.pre_call_data?.scheduled_at || a.started_at || ''
      const bt = b.pre_call_data?.scheduled_at || b.started_at || ''
      return at.localeCompare(bt)
    }

    todayCalls.sort(sortByTime)
    upcomingCalls.sort(sortByTime)

    return { today: todayCalls, upcoming: upcomingCalls }
  }, [scheduled])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Schedule</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Upcoming trial class calls with client information.
        </p>
      </div>

      {/* Today's Calls */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <Calendar className="h-4 w-4 text-blue-600" />
          <h2 className="text-base font-semibold">
            Today&apos;s Calls
            {grouped.today.length > 0 && (
              <span className="ml-2 text-sm font-normal text-muted-foreground">
                ({grouped.today.length})
              </span>
            )}
          </h2>
        </div>

        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-[200px]" />
            ))}
          </div>
        ) : grouped.today.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {grouped.today.map((call) => (
              <ScheduledCallCard key={call.id} call={call} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <Calendar className="mx-auto h-10 w-10 text-muted-foreground/40" />
              <p className="mt-3 text-sm text-muted-foreground">
                No calls scheduled for today.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Upcoming Calls */}
      {grouped.upcoming.length > 0 && (
        <div>
          <div className="mb-3 flex items-center gap-2">
            <CalendarDays className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-base font-semibold">
              Upcoming
              <span className="ml-2 text-sm font-normal text-muted-foreground">
                ({grouped.upcoming.length})
              </span>
            </h2>
          </div>

          <div className="space-y-2">
            {grouped.upcoming.map((call) => {
              const scheduledAt = call.pre_call_data?.scheduled_at || call.started_at
              const dateLabel = scheduledAt
                ? formatRelativeDate(new Date(scheduledAt))
                : ''
              const time = scheduledAt
                ? new Date(scheduledAt).toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false,
                  })
                : ''

              return (
                <Card key={call.id}>
                  <CardContent className="flex items-center gap-4 py-3">
                    <div className="shrink-0 text-right">
                      <p className="text-xs font-medium text-muted-foreground">
                        {dateLabel}
                      </p>
                      <p className="font-mono text-sm font-semibold">{time}</p>
                    </div>
                    <div className="h-8 w-px bg-border" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">
                        {call.pre_call_data?.client_name || call.title}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {call.pre_call_data?.child_name && (
                          <span>
                            {call.pre_call_data.child_name}
                            {call.pre_call_data.child_age
                              ? ` (${call.pre_call_data.child_age})`
                              : ''}
                          </span>
                        )}
                        {call.pre_call_data?.recommended_course && (
                          <span> · {call.pre_call_data.recommended_course}</span>
                        )}
                      </p>
                    </div>
                    {call.pre_call_data?.source_channel && (
                      <span className="shrink-0 text-[10px] text-muted-foreground">
                        {call.pre_call_data.source_channel}
                      </span>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

function formatRelativeDate(date: Date): string {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const target = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffDays = Math.round(
    (target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
  )

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Tomorrow'
  if (diffDays < 7) {
    return date.toLocaleDateString('en-US', { weekday: 'long' })
  }
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
