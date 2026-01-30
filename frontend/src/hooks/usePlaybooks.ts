import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Playbook, PlaybookVersion } from '@/types'

export function usePlaybooks() {
  return useQuery({
    queryKey: ['playbooks'],
    queryFn: () => api.get<Playbook[]>('/api/v1/playbooks'),
  })
}

export function usePlaybook(id: string | undefined) {
  return useQuery({
    queryKey: ['playbook', id],
    queryFn: () => api.get<Playbook>(`/api/v1/playbooks/${id}`),
    enabled: !!id,
  })
}

export function usePlaybookVersions(playbookId: string | undefined) {
  return useQuery({
    queryKey: ['playbook-versions', playbookId],
    queryFn: () => api.get<PlaybookVersion[]>(`/api/v1/playbooks/${playbookId}/versions`),
    enabled: !!playbookId,
  })
}

export function useCreatePlaybook() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { name: string; description: string }) =>
      api.post<Playbook>('/api/v1/playbooks', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playbooks'] })
    },
  })
}

export function useUpdatePlaybook() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...data }: { id: string; name?: string; description?: string; is_active?: boolean }) =>
      api.put<Playbook>(`/api/v1/playbooks/${id}`, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['playbooks'] })
      queryClient.invalidateQueries({ queryKey: ['playbook', variables.id] })
    },
  })
}

export function useCreatePlaybookVersion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ playbookId, ...data }: { playbookId: string } & Partial<PlaybookVersion>) =>
      api.post<PlaybookVersion>(`/api/v1/playbooks/${playbookId}/versions`, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['playbook-versions', variables.playbookId] })
    },
  })
}

export function usePublishVersion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ playbookId, versionId }: { playbookId: string; versionId: string }) =>
      api.post(`/api/v1/playbooks/${playbookId}/versions/${versionId}/publish`),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['playbook-versions', variables.playbookId] })
    },
  })
}
