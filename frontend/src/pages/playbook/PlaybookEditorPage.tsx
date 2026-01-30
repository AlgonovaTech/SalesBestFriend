import { useParams, useNavigate } from 'react-router-dom'
import { usePlaybook, usePlaybookVersions, useCreatePlaybookVersion, usePublishVersion } from '@/hooks/usePlaybooks'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, Save, Upload, Plus, Trash2, GripVertical } from 'lucide-react'
import { useState, useEffect } from 'react'
import { formatDate } from '@/lib/utils'
import { DocumentsTab } from '@/components/playbook/DocumentsTab'
import type { CallStage, ChecklistItem, ScoringCriterion, PlaybookVersion } from '@/types'

export function PlaybookEditorPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: playbook, isLoading: playbookLoading } = usePlaybook(id)
  const { data: versions } = usePlaybookVersions(id)
  const createVersion = useCreatePlaybookVersion()
  const publishVersion = usePublishVersion()

  // Editor state
  const [guidelines, setGuidelines] = useState('')
  const [stages, setStages] = useState<CallStage[]>([])
  const [scoringCriteria, setScoringCriteria] = useState<ScoringCriterion[]>([])
  const [dirty, setDirty] = useState(false)

  // Load latest version data
  useEffect(() => {
    if (versions && versions.length > 0) {
      const latest = versions[0]
      setGuidelines(latest.guidelines_content || '')
      setStages(latest.call_structure || [])
      setScoringCriteria(latest.scoring_criteria || [])
    }
  }, [versions])

  async function handleSave() {
    if (!id) return
    await createVersion.mutateAsync({
      playbookId: id,
      guidelines_content: guidelines,
      call_structure: stages,
      scoring_criteria: scoringCriteria,
    })
    setDirty(false)
  }

  async function handlePublish() {
    if (!id || !versions || versions.length === 0) return
    const latest = versions[0]
    await publishVersion.mutateAsync({ playbookId: id, versionId: latest.id })
  }

  // Stage management
  function addStage() {
    const newStage: CallStage = {
      id: `stage_${Date.now()}`,
      name: 'New Stage',
      order: stages.length,
      duration_minutes: 5,
      items: [],
    }
    setStages([...stages, newStage])
    setDirty(true)
  }

  function updateStage(index: number, field: keyof CallStage, value: unknown) {
    const updated = [...stages]
    updated[index] = { ...updated[index], [field]: value }
    setStages(updated)
    setDirty(true)
  }

  function removeStage(index: number) {
    setStages(stages.filter((_, i) => i !== index))
    setDirty(true)
  }

  function addItem(stageIndex: number) {
    const updated = [...stages]
    const item: ChecklistItem = {
      id: `item_${Date.now()}`,
      label: '',
      description: '',
      keywords_required: [],
      keywords_forbidden: [],
    }
    updated[stageIndex] = {
      ...updated[stageIndex],
      items: [...updated[stageIndex].items, item],
    }
    setStages(updated)
    setDirty(true)
  }

  function updateItem(
    stageIndex: number,
    itemIndex: number,
    field: keyof ChecklistItem,
    value: unknown
  ) {
    const updated = [...stages]
    const items = [...updated[stageIndex].items]
    items[itemIndex] = { ...items[itemIndex], [field]: value }
    updated[stageIndex] = { ...updated[stageIndex], items }
    setStages(updated)
    setDirty(true)
  }

  function removeItem(stageIndex: number, itemIndex: number) {
    const updated = [...stages]
    updated[stageIndex] = {
      ...updated[stageIndex],
      items: updated[stageIndex].items.filter((_, i) => i !== itemIndex),
    }
    setStages(updated)
    setDirty(true)
  }

  // Scoring criteria management
  function addCriterion() {
    setScoringCriteria([
      ...scoringCriteria,
      { name: '', max_score: 10, description: '', weight: 1 },
    ])
    setDirty(true)
  }

  function updateCriterion(index: number, field: keyof ScoringCriterion, value: unknown) {
    const updated = [...scoringCriteria]
    updated[index] = { ...updated[index], [field]: value }
    setScoringCriteria(updated)
    setDirty(true)
  }

  function removeCriterion(index: number) {
    setScoringCriteria(scoringCriteria.filter((_, i) => i !== index))
    setDirty(true)
  }

  if (playbookLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-[400px]" />
      </div>
    )
  }

  if (!playbook) {
    return <p className="text-muted-foreground">Playbook not found.</p>
  }

  const latestVersion = versions?.[0]
  const isPublished = !!latestVersion?.published_at

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate('/playbooks')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{playbook.name}</h1>
            <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
              {latestVersion && (
                <>
                  <span>v{latestVersion.version_number}</span>
                  <span>&middot;</span>
                  {isPublished ? (
                    <Badge variant="default" className="text-xs">
                      Published {formatDate(latestVersion.published_at!)}
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="text-xs">Draft</Badge>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleSave} disabled={!dirty || createVersion.isPending}>
            <Save className="mr-2 h-4 w-4" />
            Save Draft
          </Button>
          <Button onClick={handlePublish} disabled={!latestVersion || publishVersion.isPending}>
            <Upload className="mr-2 h-4 w-4" />
            Publish
          </Button>
        </div>
      </div>

      {/* Editor Tabs */}
      <Tabs defaultValue="guidelines">
        <TabsList>
          <TabsTrigger value="guidelines">Guidelines</TabsTrigger>
          <TabsTrigger value="structure">Call Structure</TabsTrigger>
          <TabsTrigger value="scoring">Scoring Criteria</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>

        {/* Guidelines Tab */}
        <TabsContent value="guidelines" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Methodology Guidelines</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={guidelines}
                onChange={(e) => { setGuidelines(e.target.value); setDirty(true) }}
                placeholder="Write your sales methodology guidelines here. Describe the approach, key principles, and best practices for your team..."
                rows={20}
                className="font-mono text-sm"
              />
              <p className="mt-2 text-xs text-muted-foreground">
                Rich text editor (TipTap) will replace this textarea in a future update.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Call Structure Tab */}
        <TabsContent value="structure" className="mt-4 space-y-4">
          {stages.map((stage, si) => (
            <Card key={stage.id}>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <GripVertical className="h-4 w-4 text-muted-foreground/50" />
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3">
                      <Input
                        value={stage.name}
                        onChange={(e) => updateStage(si, 'name', e.target.value)}
                        className="max-w-xs font-medium"
                      />
                      <div className="flex items-center gap-1">
                        <Input
                          type="number"
                          value={stage.duration_minutes ?? 0}
                          onChange={(e) => updateStage(si, 'duration_minutes', parseInt(e.target.value) || 0)}
                          className="w-20"
                        />
                        <span className="text-xs text-muted-foreground">min</span>
                      </div>
                      <Button variant="ghost" size="icon" onClick={() => removeStage(si)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {stage.items.map((item, ii) => (
                  <div key={item.id} className="flex gap-2 rounded-md border p-3">
                    <div className="flex-1 space-y-2">
                      <Input
                        value={item.label}
                        onChange={(e) => updateItem(si, ii, 'label', e.target.value)}
                        placeholder="Checklist item label"
                        className="text-sm"
                      />
                      <Textarea
                        value={item.description}
                        onChange={(e) => updateItem(si, ii, 'description', e.target.value)}
                        placeholder="Detailed description for AI detection..."
                        rows={2}
                        className="text-sm"
                      />
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <Label className="text-xs">Required Keywords</Label>
                          <Input
                            value={item.keywords_required?.join(', ') || ''}
                            onChange={(e) =>
                              updateItem(si, ii, 'keywords_required',
                                e.target.value.split(',').map((s) => s.trim()).filter(Boolean)
                              )
                            }
                            placeholder="word1, word2, word3"
                            className="text-xs"
                          />
                        </div>
                        <div>
                          <Label className="text-xs">Forbidden Keywords</Label>
                          <Input
                            value={item.keywords_forbidden?.join(', ') || ''}
                            onChange={(e) =>
                              updateItem(si, ii, 'keywords_forbidden',
                                e.target.value.split(',').map((s) => s.trim()).filter(Boolean)
                              )
                            }
                            placeholder="word1, word2"
                            className="text-xs"
                          />
                        </div>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => removeItem(si, ii)}>
                      <Trash2 className="h-3.5 w-3.5 text-muted-foreground" />
                    </Button>
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={() => addItem(si)}>
                  <Plus className="mr-1 h-3 w-3" />
                  Add Item
                </Button>
              </CardContent>
            </Card>
          ))}
          <Button variant="outline" onClick={addStage}>
            <Plus className="mr-2 h-4 w-4" />
            Add Stage
          </Button>
        </TabsContent>

        {/* Scoring Criteria Tab */}
        <TabsContent value="scoring" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Scoring Criteria</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {scoringCriteria.map((criterion, ci) => (
                <div key={ci} className="flex gap-3 rounded-md border p-3">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3">
                      <Input
                        value={criterion.name}
                        onChange={(e) => updateCriterion(ci, 'name', e.target.value)}
                        placeholder="Criterion name"
                        className="max-w-xs"
                      />
                      <div className="flex items-center gap-1">
                        <Label className="text-xs">Max</Label>
                        <Input
                          type="number"
                          value={criterion.max_score}
                          onChange={(e) => updateCriterion(ci, 'max_score', parseInt(e.target.value) || 0)}
                          className="w-20"
                        />
                      </div>
                      <div className="flex items-center gap-1">
                        <Label className="text-xs">Weight</Label>
                        <Input
                          type="number"
                          step="0.1"
                          value={criterion.weight}
                          onChange={(e) => updateCriterion(ci, 'weight', parseFloat(e.target.value) || 0)}
                          className="w-20"
                        />
                      </div>
                    </div>
                    <Textarea
                      value={criterion.description}
                      onChange={(e) => updateCriterion(ci, 'description', e.target.value)}
                      placeholder="What does this criterion evaluate?"
                      rows={2}
                      className="text-sm"
                    />
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => removeCriterion(ci)}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              ))}
              <Button variant="outline" size="sm" onClick={addCriterion}>
                <Plus className="mr-1 h-3 w-3" />
                Add Criterion
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents" className="mt-4">
          {id && <DocumentsTab playbookId={id} />}
        </TabsContent>
      </Tabs>

      {/* Version History */}
      {versions && versions.length > 0 && (
        <>
          <Separator />
          <div>
            <h2 className="text-sm font-medium">Version History</h2>
            <div className="mt-2 space-y-1">
              {versions.map((v: PlaybookVersion) => (
                <div key={v.id} className="flex items-center gap-3 text-sm">
                  <span className="font-mono text-muted-foreground">v{v.version_number}</span>
                  <span className="text-muted-foreground">{formatDate(v.created_at)}</span>
                  {v.published_at && (
                    <Badge variant="default" className="text-xs">Published</Badge>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
