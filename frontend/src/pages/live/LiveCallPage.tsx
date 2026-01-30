import { useState, useCallback, useEffect, useRef } from 'react'
import { useAudioCapture } from '@/hooks/useAudioCapture'
import { useCallWebSocket } from '@/hooks/useCallWebSocket'
import { useCreateCall } from '@/hooks/useCalls'
import { useLiveCallStore } from '@/stores/liveCallStore'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Progress } from '@/components/ui/progress'
import {
  Mic,
  MicOff,
  Clock,
  CheckCircle2,
  Circle,
  User,
  FileText,
  Lightbulb,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { cn, formatTime } from '@/lib/utils'
import type { WSCoachMessage, PreCallData, Call } from '@/types'

type ConnectionStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'

export function LiveCallPage() {
  const store = useLiveCallStore()
  const createCall = useCreateCall()
  const [wsStatus, setWsStatus] = useState<ConnectionStatus>('idle')
  const [callTitle, setCallTitle] = useState('')
  const [preCallNotes, setPreCallNotes] = useState('')
  const [preCallClientName, setPreCallClientName] = useState('')
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set())
  const timerRef = useRef<number | null>(null)

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((msg: WSCoachMessage) => {
    switch (msg.type) {
      case 'transcript':
        store.addTranscriptSegment(msg.segment)
        break
      case 'checklist':
        store.updateChecklistItem(msg.stage_id, msg.item_id, msg.completed, msg.confidence, msg.evidence)
        break
      case 'client_card':
        store.updateClientCardField(msg.field_id, msg.value, msg.confidence, msg.evidence)
        break
      case 'stage_change':
        store.setCurrentStage(msg.stage_id, msg.stage_name)
        break
      case 'coaching_tip':
        store.addCoachingTip(msg)
        break
    }
  }, [store])

  const { connect, disconnect, sendAudio } = useCallWebSocket({
    callId: store.callId,
    onMessage: handleMessage,
    onStatusChange: setWsStatus,
  })

  const { start: startCapture, stop: stopCapture } = useAudioCapture({
    onChunk: sendAudio,
  })

  // Timer
  useEffect(() => {
    if (store.isRecording) {
      timerRef.current = window.setInterval(() => {
        store.setElapsedSeconds(store.elapsedSeconds + 1)
      }, 1000)
    }
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [store.isRecording, store.elapsedSeconds])

  async function handleStart() {
    if (!callTitle.trim()) return

    // Create call in backend
    const preCallData: PreCallData | undefined =
      preCallClientName || preCallNotes
        ? { client_name: preCallClientName, notes: preCallNotes }
        : undefined

    const call: Call = await createCall.mutateAsync({
      title: callTitle.trim(),
      source: 'browser',
      pre_call_data: preCallData,
    })

    store.setCallId(call.id)
    store.setRecording(true)

    // Connect WebSocket, then start audio
    await connect()
    const handle = await startCapture()
    handle.onTrackEnded(handleStop)
  }

  function handleStop() {
    stopCapture()
    disconnect()
    store.setRecording(false)
    // Don't reset — keep data visible for review
  }

  function toggleStage(stageId: string) {
    setExpandedStages((prev) => {
      const next = new Set(prev)
      if (next.has(stageId)) next.delete(stageId)
      else next.add(stageId)
      return next
    })
  }

  const checklistStages = store.checklistProgress?.stages || []
  const totalItems = checklistStages.reduce((sum, s) => sum + s.items.length, 0)
  const completedItems = checklistStages.reduce(
    (sum, s) => sum + s.items.filter((i) => i.completed).length,
    0
  )
  const progressPercent = totalItems > 0 ? (completedItems / totalItems) * 100 : 0

  // Pre-call setup view
  if (!store.isRecording && !store.callId) {
    return (
      <div className="mx-auto max-w-lg space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Start Live Call</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Set up your call details before starting the session.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Call Setup</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="call-title">Call Title</Label>
              <Input
                id="call-title"
                placeholder="e.g. Trial Class — Budi Santoso"
                value={callTitle}
                onChange={(e) => setCallTitle(e.target.value)}
                autoFocus
              />
            </div>

            <Separator />

            <div>
              <h3 className="mb-3 text-sm font-medium">Pre-Call Client Data</h3>
              <div className="space-y-3">
                <div className="space-y-2">
                  <Label htmlFor="client-name">Client Name</Label>
                  <Input
                    id="client-name"
                    placeholder="Parent / company name"
                    value={preCallClientName}
                    onChange={(e) => setPreCallClientName(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="pre-notes">Notes / Context</Label>
                  <Textarea
                    id="pre-notes"
                    placeholder="Any context from CRM, previous calls, or prep documents..."
                    value={preCallNotes}
                    onChange={(e) => setPreCallNotes(e.target.value)}
                    rows={4}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Button
          size="lg"
          className="w-full"
          onClick={handleStart}
          disabled={!callTitle.trim() || createCall.isPending}
        >
          <Mic className="mr-2 h-5 w-5" />
          Start Recording
        </Button>

        <p className="text-center text-xs text-muted-foreground">
          You'll be asked to select a browser tab and enable "Share audio".
        </p>
      </div>
    )
  }

  // Active call / review view
  return (
    <div className="space-y-4">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold">{callTitle || 'Live Call'}</h1>
          <Badge
            variant={wsStatus === 'connected' ? 'default' : wsStatus === 'error' ? 'destructive' : 'secondary'}
          >
            {wsStatus}
          </Badge>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-mono text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            {formatTime(store.elapsedSeconds)}
          </div>
          {store.isRecording ? (
            <Button variant="destructive" onClick={handleStop}>
              <MicOff className="mr-2 h-4 w-4" />
              Stop
            </Button>
          ) : (
            <Button variant="outline" onClick={() => { store.reset(); setCallTitle('') }}>
              New Call
            </Button>
          )}
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-3">
        <Progress value={progressPercent} className="flex-1" />
        <span className="text-xs text-muted-foreground">
          {completedItems}/{totalItems} items
        </span>
      </div>

      {/* Main Layout: 3 columns */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* Left: Checklist */}
        <div className="lg:col-span-1">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <FileText className="h-4 w-4" />
                Checklist
              </CardTitle>
              {store.currentStageName && (
                <p className="text-xs text-primary">
                  Current: {store.currentStageName}
                </p>
              )}
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-320px)]">
                <div className="space-y-2 pr-3">
                  {checklistStages.map((stage) => {
                    const stageCompleted = stage.items.filter((i) => i.completed).length
                    const isExpanded = expandedStages.has(stage.stage_id)
                    const isCurrent = stage.stage_id === store.currentStageId

                    return (
                      <div key={stage.stage_id}>
                        <button
                          className={cn(
                            'flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm font-medium transition-colors',
                            isCurrent ? 'bg-primary/10 text-primary' : 'hover:bg-muted'
                          )}
                          onClick={() => toggleStage(stage.stage_id)}
                        >
                          {isExpanded ? (
                            <ChevronDown className="h-3.5 w-3.5 shrink-0" />
                          ) : (
                            <ChevronRight className="h-3.5 w-3.5 shrink-0" />
                          )}
                          <span className="flex-1 truncate">{stage.stage_name}</span>
                          <span className="text-xs text-muted-foreground">
                            {stageCompleted}/{stage.items.length}
                          </span>
                        </button>
                        {isExpanded && (
                          <div className="ml-5 mt-1 space-y-1">
                            {stage.items.map((item) => (
                              <div
                                key={item.item_id}
                                className="flex items-start gap-2 py-1"
                              >
                                {item.completed ? (
                                  <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-green-600" />
                                ) : (
                                  <Circle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground/40" />
                                )}
                                <span
                                  className={cn(
                                    'text-xs',
                                    item.completed && 'text-muted-foreground line-through'
                                  )}
                                >
                                  {item.label}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )
                  })}

                  {checklistStages.length === 0 && (
                    <p className="py-8 text-center text-xs text-muted-foreground">
                      Waiting for checklist data...
                    </p>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Center: Transcript + Coaching */}
        <div className="space-y-4 lg:col-span-1">
          {/* Coaching Tips */}
          {store.coachingTips.length > 0 && (
            <Card className="border-amber-200 bg-amber-50/50">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm text-amber-800">
                  <Lightbulb className="h-4 w-4" />
                  Coaching Tip
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-amber-900">
                  {store.coachingTips[store.coachingTips.length - 1].tip}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Live Transcript */}
          <Card className="h-full">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Live Transcript</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-400px)]">
                <div className="space-y-2 pr-3">
                  {store.transcript.map((seg) => (
                    <div key={seg.id} className="flex gap-2">
                      <span className="mt-0.5 shrink-0 font-mono text-[10px] text-muted-foreground">
                        {formatTime(Math.floor(seg.start_seconds))}
                      </span>
                      <div>
                        {seg.speaker && (
                          <span className="text-xs font-medium text-primary">
                            {seg.speaker}:{' '}
                          </span>
                        )}
                        <span className="text-sm">{seg.text}</span>
                      </div>
                    </div>
                  ))}
                  {store.transcript.length === 0 && (
                    <p className="py-8 text-center text-xs text-muted-foreground">
                      {store.isRecording
                        ? 'Listening...'
                        : 'Transcript will appear here during the call.'}
                    </p>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Right: Client Card + Pre-Call */}
        <div className="space-y-4 lg:col-span-1">
          {/* Pre-Call Briefing */}
          {(preCallClientName || preCallNotes) && (
            <Card className="border-blue-200 bg-blue-50/50">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm text-blue-800">
                  <User className="h-4 w-4" />
                  Pre-Call Briefing
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                {preCallClientName && (
                  <p className="text-sm font-medium text-blue-900">{preCallClientName}</p>
                )}
                {preCallNotes && (
                  <p className="text-xs text-blue-800">{preCallNotes}</p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Client Card */}
          <Card className="h-full">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <User className="h-4 w-4" />
                Client Card
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-400px)]">
                <div className="space-y-3 pr-3">
                  {store.clientCardData &&
                    Object.entries(store.clientCardData).map(([field, data]) => (
                      <div key={field}>
                        <p className="text-xs font-medium text-muted-foreground">
                          {field.replace(/_/g, ' ')}
                        </p>
                        <p className="mt-0.5 text-sm">{data.value || '—'}</p>
                      </div>
                    ))}
                  {(!store.clientCardData || Object.keys(store.clientCardData).length === 0) && (
                    <p className="py-8 text-center text-xs text-muted-foreground">
                      Client data will be extracted during the call.
                    </p>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
