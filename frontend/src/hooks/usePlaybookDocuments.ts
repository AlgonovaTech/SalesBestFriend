import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { PlaybookDocument, PlaybookDocumentType } from '@/types'

export function usePlaybookDocuments(
  playbookId: string | undefined,
  documentType?: PlaybookDocumentType
) {
  return useQuery({
    queryKey: ['playbook-documents', playbookId, documentType],
    queryFn: () => {
      const params = documentType ? `?document_type=${documentType}` : ''
      return api.get<PlaybookDocument[]>(
        `/api/v1/playbooks/${playbookId}/documents${params}`
      )
    },
    enabled: !!playbookId,
  })
}

export function useCreatePlaybookDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      playbookId,
      ...data
    }: {
      playbookId: string
      document_type: PlaybookDocumentType
      title: string
      description?: string
      content?: string
      sort_order?: number
    }) => api.post<PlaybookDocument>(`/api/v1/playbooks/${playbookId}/documents`, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['playbook-documents', variables.playbookId],
      })
    },
  })
}

export function useUpdatePlaybookDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      playbookId,
      documentId,
      ...data
    }: {
      playbookId: string
      documentId: string
      title?: string
      description?: string
      content?: string
      sort_order?: number
    }) =>
      api.put<PlaybookDocument>(
        `/api/v1/playbooks/${playbookId}/documents/${documentId}`,
        data
      ),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['playbook-documents', variables.playbookId],
      })
    },
  })
}

export function useDeletePlaybookDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      playbookId,
      documentId,
    }: {
      playbookId: string
      documentId: string
    }) => api.delete(`/api/v1/playbooks/${playbookId}/documents/${documentId}`),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['playbook-documents', variables.playbookId],
      })
    },
  })
}
