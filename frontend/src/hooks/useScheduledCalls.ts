import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Call, PaginatedResponse } from '@/types'

export function useScheduledCalls() {
  return useQuery({
    queryKey: ['calls', { status: 'scheduled' }],
    queryFn: () =>
      api.get<PaginatedResponse<Call>>('/api/v1/calls?status=scheduled&per_page=50'),
  })
}

export function useTodaysCalls() {
  return useQuery({
    queryKey: ['calls', { status: 'scheduled', today: true }],
    queryFn: async () => {
      const result = await api.get<PaginatedResponse<Call>>(
        '/api/v1/calls?status=scheduled&per_page=50'
      )
      // Filter for today's calls client-side based on pre_call_data.scheduled_at
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)

      const todaysCalls = result.data.filter((call) => {
        const scheduledAt = call.pre_call_data?.scheduled_at || call.started_at
        if (!scheduledAt) return false
        const date = new Date(scheduledAt)
        return date >= today && date < tomorrow
      })

      // Sort by scheduled time
      todaysCalls.sort((a, b) => {
        const aTime = a.pre_call_data?.scheduled_at || a.started_at || ''
        const bTime = b.pre_call_data?.scheduled_at || b.started_at || ''
        return aTime.localeCompare(bTime)
      })

      return todaysCalls
    },
  })
}
