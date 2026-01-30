import { useParams, useNavigate } from 'react-router-dom'
import { useCall, useCallTranscript, useCallAnalysis, useCallScores, useCallTasks, useTriggerAnalysis } from '@/hooks/useCalls'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import {
  ArrowLeft,
  Brain,
  FileText,
  BarChart3,
  CheckSquare,
  Clock,
  ThumbsUp,
  ThumbsDown,
  Target,
  Zap,
  User,
} from 'lucide-react'
import { formatDate, formatDuration, formatTime } from '@/lib/utils'
import type { CallScore, TranscriptSegment, CallTask } from '@/types'

export function CallDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: call, isLoading: callLoading } = useCall(id)
  const { data: transcript } = useCallTranscript(id)
  const { data: analysis } = useCallAnalysis(id)
  const { data: scores } = useCallScores(id)
  const { data: tasks } = useCallTasks(id)
  const triggerAnalysis = useTriggerAnalysis()

  if (callLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-[500px]" />
      </div>
    )
  }

  if (!call) {
    return <p className="text-muted-foreground">Call not found.</p>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate('/calls')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{call.title}</h1>
            <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
              <span>{formatDate(call.created_at)}</span>
              {call.duration_seconds && (
                <>
                  <span>&middot;</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {formatDuration(call.duration_seconds)}
                  </span>
                </>
              )}
              <Badge variant="secondary">{call.status}</Badge>
              <Badge variant="outline">{call.source}</Badge>
            </div>
          </div>
        </div>
        {call.status === 'completed' && !analysis && (
          <Button
            onClick={() => triggerAnalysis.mutate(call.id)}
            disabled={triggerAnalysis.isPending}
          >
            <Brain className="mr-2 h-4 w-4" />
            Run Analysis
          </Button>
        )}
      </div>

      {/* Score overview */}
      {analysis?.overall_score != null && (
        <Card>
          <CardContent className="flex items-center gap-6 py-4">
            <div className="text-center">
              <p className="text-3xl font-bold">{Math.round(analysis.overall_score)}</p>
              <p className="text-xs text-muted-foreground">Overall Score</p>
            </div>
            <Separator orientation="vertical" className="h-12" />
            <div className="flex-1">
              <div className="grid grid-cols-2 gap-x-8 gap-y-2 sm:grid-cols-4">
                {scores?.map((s: CallScore) => (
                  <div key={s.id}>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">{s.criteria_name}</span>
                      <span className="text-xs font-medium">{s.score}/{s.criteria_max_score}</span>
                    </div>
                    <Progress
                      value={(s.score / s.criteria_max_score) * 100}
                      className="mt-1 h-1.5"
                    />
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs defaultValue="analysis">
        <TabsList>
          <TabsTrigger value="analysis">
            <Brain className="mr-1.5 h-3.5 w-3.5" />
            Analysis
          </TabsTrigger>
          <TabsTrigger value="transcript">
            <FileText className="mr-1.5 h-3.5 w-3.5" />
            Transcript
          </TabsTrigger>
          <TabsTrigger value="scores">
            <BarChart3 className="mr-1.5 h-3.5 w-3.5" />
            Scores
          </TabsTrigger>
          <TabsTrigger value="tasks">
            <CheckSquare className="mr-1.5 h-3.5 w-3.5" />
            Tasks
          </TabsTrigger>
        </TabsList>

        {/* Analysis Tab */}
        <TabsContent value="analysis" className="mt-4">
          {analysis ? (
            <div className="grid gap-4 md:grid-cols-2">
              {/* Summary */}
              <Card className="md:col-span-2">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm leading-relaxed">{analysis.summary}</p>
                </CardContent>
              </Card>

              {/* What went well */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-base text-green-700">
                    <ThumbsUp className="h-4 w-4" />
                    What Went Well
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {analysis.what_went_well?.map((item: string, i: number) => (
                      <li key={i} className="flex gap-2 text-sm">
                        <span className="mt-1 text-green-500">+</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Needs improvement */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-base text-amber-700">
                    <ThumbsDown className="h-4 w-4" />
                    Needs Improvement
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {analysis.needs_improvement?.map((item: string, i: number) => (
                      <li key={i} className="flex gap-2 text-sm">
                        <span className="mt-1 text-amber-500">-</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Goals & Pain Points */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Target className="h-4 w-4" />
                    Goals Identified
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {analysis.goals_identified?.map((g: string, i: number) => (
                      <li key={i} className="text-sm">{g}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Zap className="h-4 w-4" />
                    Interest Signals
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {analysis.interest_signals?.map((s: string, i: number) => (
                      <li key={i} className="text-sm">{s}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Buyer Profile */}
              {analysis.buyer_profile_summary && (
                <Card className="md:col-span-2">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <User className="h-4 w-4" />
                      Buyer Profile
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{analysis.buyer_profile_summary}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Brain className="mx-auto h-10 w-10 text-muted-foreground/50" />
                <p className="mt-3 text-sm text-muted-foreground">
                  No analysis available yet. Run analysis after the call is completed.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Transcript Tab */}
        <TabsContent value="transcript" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              <ScrollArea className="h-[500px]">
                <div className="space-y-3 pr-4">
                  {transcript?.map((seg: TranscriptSegment) => (
                    <div key={seg.id} className="flex gap-3">
                      <span className="shrink-0 pt-0.5 font-mono text-xs text-muted-foreground">
                        {formatTime(Math.floor(seg.start_seconds))}
                      </span>
                      <div>
                        {seg.speaker && (
                          <span className="text-xs font-medium text-primary">
                            {seg.speaker}
                          </span>
                        )}
                        <p className="text-sm">{seg.text}</p>
                      </div>
                    </div>
                  ))}
                  {(!transcript || transcript.length === 0) && (
                    <p className="py-12 text-center text-sm text-muted-foreground">
                      No transcript available.
                    </p>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Scores Tab */}
        <TabsContent value="scores" className="mt-4">
          <div className="space-y-3">
            {scores?.map((s: CallScore) => (
              <Card key={s.id}>
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{s.criteria_name}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{s.reasoning}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold">{s.score}</p>
                      <p className="text-xs text-muted-foreground">/ {s.criteria_max_score}</p>
                    </div>
                  </div>
                  <Progress
                    value={(s.score / s.criteria_max_score) * 100}
                    className="mt-3 h-2"
                  />
                  {s.evidence && (
                    <p className="mt-2 text-xs italic text-muted-foreground">
                      "{s.evidence}"
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
            {(!scores || scores.length === 0) && (
              <Card>
                <CardContent className="py-12 text-center">
                  <BarChart3 className="mx-auto h-10 w-10 text-muted-foreground/50" />
                  <p className="mt-3 text-sm text-muted-foreground">
                    No scores available.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="mt-4">
          <div className="space-y-2">
            {tasks?.map((t: CallTask) => (
              <Card key={t.id}>
                <CardContent className="flex items-center justify-between py-3">
                  <div>
                    <p className="text-sm font-medium">{t.title}</p>
                    {t.due_date && (
                      <p className="text-xs text-muted-foreground">
                        Due: {t.due_date}
                      </p>
                    )}
                  </div>
                  <Badge variant={t.status === 'completed' ? 'default' : 'secondary'}>
                    {t.status}
                  </Badge>
                </CardContent>
              </Card>
            ))}
            {(!tasks || tasks.length === 0) && (
              <Card>
                <CardContent className="py-12 text-center">
                  <CheckSquare className="mx-auto h-10 w-10 text-muted-foreground/50" />
                  <p className="mt-3 text-sm text-muted-foreground">
                    No action items yet.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
