import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, Trash2, FileText, Pencil, X, Check } from 'lucide-react'
import {
  usePlaybookDocuments,
  useCreatePlaybookDocument,
  useUpdatePlaybookDocument,
  useDeletePlaybookDocument,
} from '@/hooks/usePlaybookDocuments'
import type { PlaybookDocument, PlaybookDocumentType } from '@/types'

interface DocumentsTabProps {
  playbookId: string
}

const DOC_TYPE_LABELS: Record<PlaybookDocumentType, string> = {
  call: 'Call Documents',
  analysis: 'Analysis Documents',
  analytics: 'Analytics Documents',
}

const DOC_TYPE_DESCRIPTIONS: Record<PlaybookDocumentType, string> = {
  call: 'Reference materials used during live calls — scripts, objection handling, product info.',
  analysis: 'Instructions and criteria used for post-call analysis by the AI.',
  analytics: 'Templates and parameters for generating call analytics and reports.',
}

function DocumentCard({
  doc,
  playbookId,
}: {
  doc: PlaybookDocument
  playbookId: string
}) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(doc.title)
  const [description, setDescription] = useState(doc.description)
  const [content, setContent] = useState(doc.content)
  const updateDoc = useUpdatePlaybookDocument()
  const deleteDoc = useDeletePlaybookDocument()

  function handleSave() {
    updateDoc.mutate(
      { playbookId, documentId: doc.id, title, description, content },
      { onSuccess: () => setEditing(false) }
    )
  }

  function handleCancel() {
    setTitle(doc.title)
    setDescription(doc.description)
    setContent(doc.content)
    setEditing(false)
  }

  function handleDelete() {
    deleteDoc.mutate({ playbookId, documentId: doc.id })
  }

  if (editing) {
    return (
      <Card>
        <CardContent className="space-y-3 pt-4">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Document title"
            className="font-medium"
          />
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short description (optional)"
            className="text-sm"
          />
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Document content — instructions, scripts, criteria..."
            rows={8}
            className="font-mono text-sm"
          />
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={handleSave}
              disabled={!title.trim() || updateDoc.isPending}
            >
              <Check className="mr-1 h-3 w-3" />
              Save
            </Button>
            <Button size="sm" variant="ghost" onClick={handleCancel}>
              <X className="mr-1 h-3 w-3" />
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="group">
      <CardContent className="pt-4">
        <div className="flex items-start justify-between">
          <div className="flex gap-3">
            <FileText className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-tight">{doc.title}</p>
              {doc.description && (
                <p className="text-xs text-muted-foreground">{doc.description}</p>
              )}
              {doc.content && (
                <p className="mt-2 line-clamp-3 whitespace-pre-wrap text-xs text-muted-foreground/80">
                  {doc.content}
                </p>
              )}
            </div>
          </div>
          <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setEditing(true)}>
              <Pencil className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={handleDelete}
              disabled={deleteDoc.isPending}
            >
              <Trash2 className="h-3 w-3 text-destructive" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function DocumentTypeSection({
  playbookId,
  docType,
}: {
  playbookId: string
  docType: PlaybookDocumentType
}) {
  const { data: documents, isLoading } = usePlaybookDocuments(playbookId, docType)
  const createDoc = useCreatePlaybookDocument()
  const [adding, setAdding] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [newContent, setNewContent] = useState('')

  function handleAdd() {
    if (!newTitle.trim()) return
    createDoc.mutate(
      {
        playbookId,
        document_type: docType,
        title: newTitle.trim(),
        description: newDescription.trim(),
        content: newContent.trim(),
      },
      {
        onSuccess: () => {
          setNewTitle('')
          setNewDescription('')
          setNewContent('')
          setAdding(false)
        },
      }
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-20" />
        <Skeleton className="h-20" />
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground">{DOC_TYPE_DESCRIPTIONS[docType]}</p>

      {documents?.map((doc) => (
        <DocumentCard key={doc.id} doc={doc} playbookId={playbookId} />
      ))}

      {adding ? (
        <Card>
          <CardContent className="space-y-3 pt-4">
            <Input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Document title"
              className="font-medium"
              autoFocus
            />
            <Input
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              placeholder="Short description (optional)"
              className="text-sm"
            />
            <Textarea
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              placeholder="Document content..."
              rows={6}
              className="font-mono text-sm"
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleAdd}
                disabled={!newTitle.trim() || createDoc.isPending}
              >
                <Check className="mr-1 h-3 w-3" />
                Add Document
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setAdding(false)
                  setNewTitle('')
                  setNewDescription('')
                  setNewContent('')
                }}
              >
                <X className="mr-1 h-3 w-3" />
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Button variant="outline" size="sm" onClick={() => setAdding(true)}>
          <Plus className="mr-1 h-3 w-3" />
          Add Document
        </Button>
      )}

      {!adding && (!documents || documents.length === 0) && (
        <div className="rounded-lg border border-dashed p-6 text-center">
          <FileText className="mx-auto h-8 w-8 text-muted-foreground/40" />
          <p className="mt-2 text-sm text-muted-foreground">No documents yet</p>
          <p className="text-xs text-muted-foreground/60">
            Add documents to provide context for this category.
          </p>
        </div>
      )}
    </div>
  )
}

export function DocumentsTab({ playbookId }: DocumentsTabProps) {
  return (
    <Tabs defaultValue="call">
      <TabsList>
        <TabsTrigger value="call">Call</TabsTrigger>
        <TabsTrigger value="analysis">Analysis</TabsTrigger>
        <TabsTrigger value="analytics">Analytics</TabsTrigger>
      </TabsList>
      {(Object.keys(DOC_TYPE_LABELS) as PlaybookDocumentType[]).map((docType) => (
        <TabsContent key={docType} value={docType} className="mt-4">
          <DocumentTypeSection playbookId={playbookId} docType={docType} />
        </TabsContent>
      ))}
    </Tabs>
  )
}
