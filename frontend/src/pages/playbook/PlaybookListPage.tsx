import { Link } from 'react-router-dom'
import { usePlaybooks, useCreatePlaybook } from '@/hooks/usePlaybooks'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, BookOpen } from 'lucide-react'
import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { formatDate } from '@/lib/utils'
import type { Playbook } from '@/types'

export function PlaybookListPage() {
  const { data: playbooks, isLoading } = usePlaybooks()
  const createPlaybook = useCreatePlaybook()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  async function handleCreate() {
    if (!name.trim()) return
    await createPlaybook.mutateAsync({ name: name.trim(), description: description.trim() })
    setDialogOpen(false)
    setName('')
    setDescription('')
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Playbooks</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sales methodology playbooks define call structure, scoring, and coaching rules.
          </p>
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Playbook
        </Button>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading &&
          Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-5 w-40" />
                <Skeleton className="mt-1 h-4 w-60" />
              </CardHeader>
            </Card>
          ))}

        {playbooks?.map((pb: Playbook) => (
          <Link key={pb.id} to={`/playbooks/${pb.id}`}>
            <Card className="transition-colors hover:border-primary/30">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-muted-foreground" />
                    <CardTitle className="text-base">{pb.name}</CardTitle>
                  </div>
                  <Badge variant={pb.is_active ? 'default' : 'secondary'}>
                    {pb.is_active ? 'Active' : 'Draft'}
                  </Badge>
                </div>
                <CardDescription className="line-clamp-2">
                  {pb.description || 'No description'}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <p className="text-xs text-muted-foreground">
                  Created {formatDate(pb.created_at)}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}

        {!isLoading && playbooks?.length === 0 && (
          <div className="col-span-full py-12 text-center">
            <BookOpen className="mx-auto h-10 w-10 text-muted-foreground/50" />
            <p className="mt-3 text-sm text-muted-foreground">
              No playbooks yet. Create one to define your sales methodology.
            </p>
          </div>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Playbook</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="pb-name">Name</Label>
              <Input
                id="pb-name"
                placeholder="e.g. Trial Class Sales v3"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pb-desc">Description</Label>
              <Textarea
                id="pb-desc"
                placeholder="Describe the methodology..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={!name.trim() || createPlaybook.isPending}>
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
