import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Upload, Youtube, Loader2 } from 'lucide-react'
import { useUploadCall, useUploadYouTube } from '@/hooks/useCalls'
import { usePlaybooks, usePlaybookVersions } from '@/hooks/usePlaybooks'

interface UploadCallDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function UploadCallDialog({ open, onOpenChange }: UploadCallDialogProps) {
  const [tab, setTab] = useState<'file' | 'youtube'>('file')
  const [title, setTitle] = useState('')
  const [language, setLanguage] = useState('id')
  const [file, setFile] = useState<File | null>(null)
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [playbookId, setPlaybookId] = useState('')
  const [versionId, setVersionId] = useState('')

  const uploadCall = useUploadCall()
  const uploadYoutube = useUploadYouTube()
  const { data: playbooks } = usePlaybooks()
  const { data: versions } = usePlaybookVersions(playbookId || undefined)

  const isLoading = uploadCall.isPending || uploadYoutube.isPending

  // Auto-select latest published version
  const publishedVersion = versions?.find((v) => v.published_at) || versions?.[0]

  function handlePlaybookChange(id: string) {
    setPlaybookId(id)
    setVersionId('')
  }

  function resetForm() {
    setTitle('')
    setFile(null)
    setYoutubeUrl('')
    setPlaybookId('')
    setVersionId('')
  }

  async function handleSubmit() {
    const selectedVersion = versionId || publishedVersion?.id || ''

    if (tab === 'file' && file) {
      await uploadCall.mutateAsync({
        file,
        title: title || file.name,
        language,
        playbook_version_id: selectedVersion || undefined,
      })
    } else if (tab === 'youtube' && youtubeUrl) {
      await uploadYoutube.mutateAsync({
        youtube_url: youtubeUrl,
        title: title || undefined,
        language,
        playbook_version_id: selectedVersion || undefined,
      })
    }

    resetForm()
    onOpenChange(false)
  }

  const canSubmit =
    !isLoading && ((tab === 'file' && file) || (tab === 'youtube' && youtubeUrl.trim()))

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Upload Call</DialogTitle>
        </DialogHeader>

        <Tabs value={tab} onValueChange={(v) => setTab(v as 'file' | 'youtube')}>
          <TabsList className="w-full">
            <TabsTrigger value="file" className="flex-1">
              <Upload className="mr-1.5 h-3.5 w-3.5" />
              File
            </TabsTrigger>
            <TabsTrigger value="youtube" className="flex-1">
              <Youtube className="mr-1.5 h-3.5 w-3.5" />
              YouTube
            </TabsTrigger>
          </TabsList>

          <TabsContent value="file" className="mt-4 space-y-4">
            <div className="space-y-2">
              <Label>Audio / Video File</Label>
              <Input
                type="file"
                accept="audio/*,video/*,.mp3,.wav,.mp4,.webm,.m4a,.ogg"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              {file && (
                <p className="text-xs text-muted-foreground">
                  {file.name} ({(file.size / 1024 / 1024).toFixed(1)} MB)
                </p>
              )}
            </div>
          </TabsContent>

          <TabsContent value="youtube" className="mt-4 space-y-4">
            <div className="space-y-2">
              <Label>YouTube URL</Label>
              <Input
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="https://youtube.com/watch?v=... or https://youtu.be/..."
              />
            </div>
          </TabsContent>
        </Tabs>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Title (optional)</Label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Call title"
            />
          </div>

          <div className="space-y-2">
            <Label>Language</Label>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="id">Bahasa Indonesia</SelectItem>
                <SelectItem value="es">Espa&ntilde;ol</SelectItem>
                <SelectItem value="ms">Bahasa Melayu</SelectItem>
                <SelectItem value="en">English</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Playbook (optional)</Label>
            <Select value={playbookId} onValueChange={handlePlaybookChange}>
              <SelectTrigger>
                <SelectValue placeholder="Select playbook..." />
              </SelectTrigger>
              <SelectContent>
                {playbooks?.map((pb) => (
                  <SelectItem key={pb.id} value={pb.id}>
                    {pb.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!canSubmit}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {tab === 'youtube' ? 'Process YouTube' : 'Upload & Analyze'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
