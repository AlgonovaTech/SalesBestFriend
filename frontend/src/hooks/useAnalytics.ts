import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { OverviewStats, UserScoreSummary, RadarDataPoint } from '@/types'

export function useOverviewStats() {
  return useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => api.get<OverviewStats>('/api/v1/analytics/overview'),
  })
}

export function useTeamAnalytics() {
  return useQuery({
    queryKey: ['analytics', 'team'],
    queryFn: () => api.get<UserScoreSummary[]>('/api/v1/analytics/team'),
  })
}

export function useUserAnalytics(userId: string | undefined) {
  return useQuery({
    queryKey: ['analytics', 'user', userId],
    queryFn: () => api.get<UserScoreSummary>(`/api/v1/analytics/user/${userId}`),
    enabled: !!userId,
  })
}

export function useRadarData(userId: string | undefined) {
  return useQuery({
    queryKey: ['analytics', 'radar', userId],
    queryFn: () => api.get<RadarDataPoint[]>(`/api/v1/analytics/radar/${userId}`),
    enabled: !!userId,
  })
}
