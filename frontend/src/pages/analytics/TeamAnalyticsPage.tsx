import { useState } from 'react'
import { useTeamAnalytics, useRadarData } from '@/hooks/useAnalytics'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'
import { BarChart3, Users, Trophy } from 'lucide-react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

export function TeamAnalyticsPage() {
  const { data: teamData, isLoading } = useTeamAnalytics()
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null)
  const { data: radarData } = useRadarData(selectedUserId ?? undefined)

  // Select first user by default
  if (!selectedUserId && teamData && teamData.length > 0) {
    setSelectedUserId(teamData[0].user_id)
  }

  const selectedUser = teamData?.find((u) => u.user_id === selectedUserId)

  // Sort by average score desc
  const sortedTeam = [...(teamData || [])].sort((a, b) => b.average_score - a.average_score)

  const radarChartData = radarData?.map((d) => ({
    criteria: d.criteria,
    score: d.score,
    fullMark: d.max,
  })) || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Team Analytics</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Performance overview, radar charts, and skill breakdown.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Radar Chart */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <BarChart3 className="h-4 w-4" />
              Skills Radar
              {selectedUser && (
                <Badge variant="secondary" className="ml-2 text-xs">
                  {selectedUser.full_name}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {radarChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={320}>
                <RadarChart data={radarChartData}>
                  <PolarGrid stroke="hsl(var(--border))" />
                  <PolarAngleAxis
                    dataKey="criteria"
                    tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <PolarRadiusAxis
                    angle={30}
                    tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <Radar
                    dataKey="score"
                    stroke="hsl(var(--primary))"
                    fill="hsl(var(--primary))"
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-[320px] items-center justify-center">
                <p className="text-sm text-muted-foreground">
                  {isLoading ? 'Loading...' : 'Select a team member to see their radar chart.'}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Leaderboard */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Trophy className="h-4 w-4" />
              Leaderboard
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-12" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {sortedTeam.map((member, index) => {
                  const initials = member.full_name
                    .split(' ')
                    .map((n) => n[0])
                    .join('')
                    .toUpperCase()
                    .slice(0, 2)

                  return (
                    <button
                      key={member.user_id}
                      className={`flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left transition-colors ${
                        selectedUserId === member.user_id
                          ? 'bg-primary/10 ring-1 ring-primary/20'
                          : 'hover:bg-muted'
                      }`}
                      onClick={() => setSelectedUserId(member.user_id)}
                    >
                      <span className="w-5 text-center text-xs font-medium text-muted-foreground">
                        {index + 1}
                      </span>
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="text-xs">
                          {initials}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="truncate text-sm font-medium">
                          {member.full_name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {member.total_calls} calls
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold">
                          {member.average_score.toFixed(1)}
                        </p>
                      </div>
                    </button>
                  )
                })}

                {sortedTeam.length === 0 && (
                  <p className="py-8 text-center text-sm text-muted-foreground">
                    No team data available yet.
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Skill Matrix Table */}
      {selectedUser && selectedUser.scores_by_criteria.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Users className="h-4 w-4" />
              Skill Breakdown — {selectedUser.full_name}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Criteria</TableHead>
                  <TableHead className="w-32">Score</TableHead>
                  <TableHead className="w-48">Progress</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {selectedUser.scores_by_criteria.map((sc) => (
                  <TableRow key={sc.criteria_name}>
                    <TableCell className="font-medium">{sc.criteria_name}</TableCell>
                    <TableCell>
                      {sc.average_score.toFixed(1)} / {sc.max_score}
                    </TableCell>
                    <TableCell>
                      <Progress
                        value={(sc.average_score / sc.max_score) * 100}
                        className="h-2"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
