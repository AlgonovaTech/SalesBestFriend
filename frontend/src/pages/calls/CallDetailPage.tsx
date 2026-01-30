import { useParams, useNavigate } from 'react-router-dom'
import { useCall, useCallTranscript, useCallAnalysis, useCallScores, useCallTasks, useTriggerAnalysis, useCallPolling } from '@/hooks/useCalls'
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
  UserCircle,
  Loader2,
  Phone,
  Mail,
  GraduationCap,
  MessageSquare,
  Globe,
  BookOpen,
} from 'lucide-react'
import { formatDate, formatDuration, formatTime } from '@/lib/utils'
import type { CallScore, TranscriptSegment, CallTask } from '@/types'

const PROCESSING_STEPS = ['queued', 'downloading', 'transcribing', 'analyzing', 'storing', 'done']

function ProcessingStepLabel(step: string) {
  const labels: Record<string, string> = {
    queued: 'Queued',
    downloading: 'Downloading audio...',
    transcribing: 'Transcribing...',
    analyzing: 'AI analysis...',
    storing: 'Saving results...',
    done: 'Complete',
  }
  return labels[step] || step
}

export function CallDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: call, isLoading: callLoading } = useCall(id)

  // Auto-poll when processing
  const isProcessing = call?.status === 'processing'
  const { data: polledCall } = useCallPolling(id, isProcessing)
  const currentCall = polledCall || call

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

  if (!currentCall) {
    return <p className="text-muted-foreground">Call not found.</p>
  }

  const processingStepIndex = currentCall.processing_step
    ? PROCESSING_STEPS.indexOf(currentCall.processing_step.replace('failed:', ''))
    : -1
  const processingProgress = processingStepIndex >= 0
    ? Math.round((processingStepIndex / (PROCESSING_STEPS.length - 1)) * 100)
    : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate('/calls')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{currentCall.title}</h1>
            <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
              <span>{formatDate(currentCall.created_at)}</span>
              {currentCall.duration_seconds && (
                <>
                  <span>&middot;</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {formatDuration(currentCall.duration_seconds)}
                  </span>
                </>
              )}
              <Badge variant="secondary">{currentCall.status}</Badge>
              <Badge variant="outline">{currentCall.source}</Badge>
            </div>
          </div>
        </div>
        {currentCall.status === 'completed' && !analysis && (
          <Button
            onClick={() => triggerAnalysis.mutate(currentCall.id)}
            disabled={triggerAnalysis.isPending}
          >
            <Brain className="mr-2 h-4 w-4" />
            Run Analysis
          </Button>
        )}
      </div>

      {/* Processing Progress */}
      {currentCall.status === 'processing' && currentCall.processing_step && (
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
              <div className="flex-1">
                <p className="text-sm font-medium">
                  {ProcessingStepLabel(currentCall.processing_step)}
                </p>
                <Progress value={processingProgress} className="mt-2 h-1.5" />
              </div>
              <span className="text-xs text-muted-foreground">{processingProgress}%</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Failed state */}
      {currentCall.status === 'failed' && (
        <Card className="border-red-200">
          <CardContent className="py-4 text-center">
            <p className="text-sm text-red-600">
              Processing failed{currentCall.processing_step?.startsWith('failed:')
                ? `: ${currentCall.processing_step.replace('failed:', '')}`
                : '.'}
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-2"
              onClick={() => triggerAnalysis.mutate(currentCall.id)}
              disabled={triggerAnalysis.isPending}
            >
              Retry Analysis
            </Button>
          </CardContent>
        </Card>
      )}

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
          {currentCall.pre_call_data && Object.keys(currentCall.pre_call_data).length > 0 && (
            <TabsTrigger value="client-info">
              <UserCircle className="mr-1.5 h-3.5 w-3.5" />
              Client Info
            </TabsTrigger>
          )}
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

        {/* Client Info Tab */}
        {currentCall.pre_call_data && Object.keys(currentCall.pre_call_data).length > 0 && (
          <TabsContent value="client-info" className="mt-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Contact Details */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <UserCircle className="h-4 w-4" />
                    Contact Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {currentCall.pre_call_data.client_name && (
                    <div className="flex items-center gap-3">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-xs text-muted-foreground">Client Name</p>
                        <p className="text-sm font-medium">{currentCall.pre_call_data.client_name}</p>
                      </div>
                    </div>
                  )}
                  {currentCall.pre_call_data.client_phone && (
                    <div className="flex items-center gap-3">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-xs text-muted-foreground">Phone</p>
                        <p className="text-sm font-medium">{currentCall.pre_call_data.client_phone}</p>
                      </div>
                    </div>
                  )}
                  {currentCall.pre_call_data.client_email && (
                    <div className="flex items-center gap-3">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-xs text-muted-foreground">Email</p>
                        <p className="text-sm font-medium">{currentCall.pre_call_data.client_email}</p>
                      </div>
                    </div>
                  )}
                  {currentCall.pre_call_data.source_channel && (
                    <div className="flex items-center gap-3">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-xs text-muted-foreground">Source Channel</p>
                        <p className="text-sm font-medium">{currentCall.pre_call_data.source_channel}</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Child / Student Info */}
              {(currentCall.pre_call_data.child_name || currentCall.pre_call_data.child_age) && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <GraduationCap className="h-4 w-4" />
                      Student Info
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {currentCall.pre_call_data.child_name && (
                      <div>
                        <p className="text-xs text-muted-foreground">Name</p>
                        <p className="text-sm font-medium">{currentCall.pre_call_data.child_name}</p>
                      </div>
                    )}
                    {currentCall.pre_call_data.child_age && (
                      <div>
                        <p className="text-xs text-muted-foreground">Age</p>
                        <p className="text-sm font-medium">{currentCall.pre_call_data.child_age} tahun</p>
                      </div>
                    )}
                    {currentCall.pre_call_data.school_level && (
                      <div>
                        <p className="text-xs text-muted-foreground">School Level</p>
                        <p className="text-sm font-medium">{currentCall.pre_call_data.school_level}</p>
                      </div>
                    )}
                    {currentCall.pre_call_data.interests && currentCall.pre_call_data.interests.length > 0 && (
                      <div>
                        <p className="text-xs text-muted-foreground">Interests</p>
                        <div className="mt-1 flex flex-wrap gap-1.5">
                          {currentCall.pre_call_data.interests.map((interest: string, i: number) => (
                            <Badge key={i} variant="secondary" className="text-xs">
                              {interest}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Course Recommendation */}
              {(currentCall.pre_call_data.recommended_course || currentCall.pre_call_data.recommended_reason) && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <BookOpen className="h-4 w-4" />
                      Course Recommendation
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {currentCall.pre_call_data.recommended_course && (
                      <div>
                        <p className="text-xs text-muted-foreground">Recommended Course</p>
                        <p className="text-sm font-medium">{currentCall.pre_call_data.recommended_course}</p>
                      </div>
                    )}
                    {currentCall.pre_call_data.recommended_reason && (
                      <div>
                        <p className="text-xs text-muted-foreground">Reason</p>
                        <p className="text-sm leading-relaxed">{currentCall.pre_call_data.recommended_reason}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Notes */}
              {currentCall.pre_call_data.notes && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <MessageSquare className="h-4 w-4" />
                      Notes
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm leading-relaxed">{currentCall.pre_call_data.notes}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}
