import { useNavigate } from 'react-router-dom'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Clock,
  Phone,
  User,
  GraduationCap,
  MessageSquare,
  ChevronRight,
} from 'lucide-react'
import type { Call } from '@/types'

interface ScheduledCallCardProps {
  call: Call
  compact?: boolean
}

export function ScheduledCallCard({ call, compact = false }: ScheduledCallCardProps) {
  const navigate = useNavigate()
  const pre = call.pre_call_data

  const scheduledAt = pre?.scheduled_at || call.started_at
  const time = scheduledAt
    ? new Date(scheduledAt).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      })
    : '--:--'

  const handleStartCall = () => {
    // Navigate to live call with pre-filled data
    navigate('/live', {
      state: {
        preCallData: pre,
        title: call.title,
        scheduledCallId: call.id,
      },
    })
  }

  if (compact) {
    return (
      <button
        onClick={() => navigate(`/calls/${call.id}`)}
        className="flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left transition-colors hover:bg-muted"
      >
        <span className="shrink-0 font-mono text-xs font-medium text-muted-foreground">
          {time}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium">
            {pre?.client_name || call.title}
          </p>
          <p className="truncate text-xs text-muted-foreground">
            {pre?.child_name && `${pre.child_name} (${pre.child_age})`}
            {pre?.recommended_course && ` · ${pre.recommended_course}`}
          </p>
        </div>
        <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
      </button>
    )
  }

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-4">
        {/* Time + Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="font-mono text-sm font-semibold">{time}</span>
          </div>
          {pre?.source_channel && (
            <Badge variant="outline" className="text-[10px]">
              {pre.source_channel}
            </Badge>
          )}
        </div>

        {/* Client Info */}
        <div className="mt-3 space-y-1.5">
          <div className="flex items-center gap-2">
            <User className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-sm font-medium">
              {pre?.client_name || 'Unknown Client'}
            </span>
          </div>

          {pre?.child_name && (
            <p className="ml-5.5 text-xs text-muted-foreground">
              {pre.child_name}
              {pre.child_age ? ` (${pre.child_age} tahun)` : ''}
              {pre?.school_level ? ` · ${pre.school_level}` : ''}
            </p>
          )}

          {pre?.recommended_course && (
            <div className="flex items-start gap-2">
              <GraduationCap className="mt-0.5 h-3.5 w-3.5 text-blue-500" />
              <div>
                <p className="text-xs font-medium text-blue-600">
                  {pre.recommended_course}
                </p>
                {pre.recommended_reason && (
                  <p className="mt-0.5 text-[11px] leading-tight text-muted-foreground">
                    {pre.recommended_reason.length > 80
                      ? pre.recommended_reason.slice(0, 80) + '...'
                      : pre.recommended_reason}
                  </p>
                )}
              </div>
            </div>
          )}

          {pre?.notes && (
            <div className="flex items-start gap-2">
              <MessageSquare className="mt-0.5 h-3.5 w-3.5 text-muted-foreground" />
              <p className="text-[11px] text-muted-foreground">
                {pre.notes.length > 60
                  ? pre.notes.slice(0, 60) + '...'
                  : pre.notes}
              </p>
            </div>
          )}
        </div>

        {/* Action */}
        <div className="mt-3 flex gap-2">
          <Button
            size="sm"
            className="flex-1"
            onClick={handleStartCall}
          >
            <Phone className="mr-1.5 h-3.5 w-3.5" />
            Start Call
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => navigate(`/calls/${call.id}`)}
          >
            View
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
