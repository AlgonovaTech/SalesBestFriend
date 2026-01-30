import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Call, PaginatedResponse, TranscriptSegment, CallAnalysis, CallScore, CallTask } from '@/types'

interface CallsFilters {
  status?: string
  source?: string
  tag_id?: string
  search?: string
  page?: number
  per_page?: number
}

export function useCalls(filters: CallsFilters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '') params.set(key, String(value))
  })
  const query = params.toString()

  return useQuery({
    queryKey: ['calls', filters],
    queryFn: () => api.get<PaginatedResponse<Call>>(`/api/v1/calls?${query}`),
  })
}

export function useCall(callId: string | undefined) {
  return useQuery({
    queryKey: ['call', callId],
    queryFn: () => api.get<Call>(`/api/v1/calls/${callId}`),
    enabled: !!callId,
  })
}

export function useCallTranscript(callId: string | undefined) {
  return useQuery({
    queryKey: ['call-transcript', callId],
    queryFn: () => api.get<TranscriptSegment[]>(`/api/v1/calls/${callId}/transcript`),
    enabled: !!callId,
  })
}

export function useCallAnalysis(callId: string | undefined) {
  return useQuery({
    queryKey: ['call-analysis', callId],
    queryFn: () => api.get<CallAnalysis>(`/api/v1/calls/${callId}/analysis`),
    enabled: !!callId,
  })
}

export function useCallScores(callId: string | undefined) {
  return useQuery({
    queryKey: ['call-scores', callId],
    queryFn: () => api.get<CallScore[]>(`/api/v1/calls/${callId}/scores`),
    enabled: !!callId,
  })
}

export function useCallTasks(callId: string | undefined) {
  return useQuery({
    queryKey: ['call-tasks', callId],
    queryFn: () => api.get<CallTask[]>(`/api/v1/calls/${callId}/tasks`),
    enabled: !!callId,
  })
}

export function useCreateCall() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { title: string; source: string; language?: string; pre_call_data?: Record<string, unknown> }) =>
      api.post<Call>('/api/v1/calls', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calls'] })
    },
  })
}

export function useTriggerAnalysis() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (callId: string) =>
      api.post<{ status: string; call_id: string }>(`/api/v1/calls/${callId}/analyze`),
    onSuccess: (_data, callId) => {
      queryClient.invalidateQueries({ queryKey: ['call-analysis', callId] })
      queryClient.invalidateQueries({ queryKey: ['call-scores', callId] })
      queryClient.invalidateQueries({ queryKey: ['call', callId] })
    },
  })
}

export function useUploadCall() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      file: File
      title?: string
      language?: string
      playbook_version_id?: string
    }) => {
      const formData = new FormData()
      formData.append('file', data.file)
      if (data.title) formData.append('title', data.title)
      if (data.language) formData.append('language', data.language)
      if (data.playbook_version_id) formData.append('playbook_version_id', data.playbook_version_id)
      return api.upload<Call>('/api/v1/calls/upload', formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calls'] })
    },
  })
}

export function useUploadYouTube() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      youtube_url: string
      title?: string
      language?: string
      playbook_version_id?: string
    }) => api.post<Call>('/api/v1/calls/upload-youtube', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calls'] })
    },
  })
}

export function useCallPolling(callId: string | undefined, enabled: boolean = false) {
  return useQuery({
    queryKey: ['call', callId],
    queryFn: () => api.get<Call>(`/api/v1/calls/${callId}`),
    enabled: !!callId && enabled,
    refetchInterval: 3000,
  })
}
