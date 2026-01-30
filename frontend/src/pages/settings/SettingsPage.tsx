import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useAuthStore } from '@/stores/authStore'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Save, Loader2 } from 'lucide-react'

export function SettingsPage() {
  const { profile } = useAuth()
  const setProfile = useAuthStore((s) => s.setProfile)
  const [fullName, setFullName] = useState(profile?.full_name ?? '')
  const [timezone, setTimezone] = useState(profile?.timezone ?? 'UTC')
  const [langPref, setLangPref] = useState(profile?.language_preference ?? 'en')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  async function handleSave() {
    if (!profile) return
    setSaving(true)
    setSaved(false)

    const { data, error } = await supabase
      .from('user_profiles')
      .update({
        full_name: fullName,
        timezone,
        language_preference: langPref,
      })
      .eq('id', profile.id)
      .select()
      .single()

    if (!error && data) {
      setProfile(data as typeof profile)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    }
    setSaving(false)
  }

  const initials = profile?.full_name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) ?? '?'

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage your profile and preferences.
        </p>
      </div>

      {/* Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Profile</CardTitle>
          <CardDescription>Your personal information and display settings.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarFallback className="text-lg">{initials}</AvatarFallback>
            </Avatar>
            <div>
              <p className="font-medium">{profile?.full_name}</p>
              <Badge variant="secondary" className="mt-1">
                {profile?.role?.replace('_', ' ')}
              </Badge>
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <Label htmlFor="full-name">Full Name</Label>
            <Input
              id="full-name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Language Preference</Label>
              <Select value={langPref} onValueChange={setLangPref}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="id">Bahasa Indonesia</SelectItem>
                  <SelectItem value="es">Espa&ntilde;ol</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Timezone</Label>
              <Select value={timezone} onValueChange={setTimezone}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC">UTC</SelectItem>
                  <SelectItem value="Asia/Jakarta">Asia/Jakarta (WIB)</SelectItem>
                  <SelectItem value="Asia/Kuala_Lumpur">Asia/Kuala Lumpur</SelectItem>
                  <SelectItem value="America/Mexico_City">America/Mexico City</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Save className="mr-2 h-4 w-4" />
              )}
              Save Changes
            </Button>
            {saved && (
              <span className="text-sm text-green-600">Saved</span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Team Info (read-only) */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Organization</CardTitle>
          <CardDescription>Your team and organization details.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <p className="text-xs text-muted-foreground">Organization ID</p>
            <p className="font-mono text-sm">{profile?.organization_id}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Team ID</p>
            <p className="font-mono text-sm">{profile?.team_id}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Role</p>
            <p className="text-sm">{profile?.role?.replace('_', ' ')}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
