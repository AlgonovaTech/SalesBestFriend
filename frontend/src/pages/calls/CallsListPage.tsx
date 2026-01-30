import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCalls } from '@/hooks/useCalls'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Search, Phone, ChevronLeft, ChevronRight, Upload } from 'lucide-react'
import { formatDate, formatDuration } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { UploadCallDialog } from '@/components/calls/UploadCallDialog'
import type { Call } from '@/types'

const statusColors: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-700',
  live: 'bg-green-100 text-green-700',
  processing: 'bg-amber-100 text-amber-700',
  completed: 'bg-slate-100 text-slate-700',
  failed: 'bg-red-100 text-red-700',
}

export function CallsListPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const [uploadOpen, setUploadOpen] = useState(false)

  const { data, isLoading } = useCalls({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    per_page: 20,
  })

  const calls = data?.data || []
  const total = data?.total || 0
  const totalPages = Math.ceil(total / 20)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Calls</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {total} total calls
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setUploadOpen(true)}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Call
          </Button>
          <Link to="/live">
            <Button>
              <Phone className="mr-2 h-4 w-4" />
              New Call
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search calls..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v === 'all' ? '' : v); setPage(1) }}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="live">Live</SelectItem>
            <SelectItem value="processing">Processing</SelectItem>
            <SelectItem value="scheduled">Scheduled</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Date</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading &&
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                </TableRow>
              ))}

            {calls.map((call: Call) => (
              <TableRow key={call.id} className="cursor-pointer">
                <TableCell>
                  <Link
                    to={`/calls/${call.id}`}
                    className="font-medium hover:underline"
                  >
                    {call.title}
                  </Link>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1.5">
                    <Badge
                      variant="secondary"
                      className={cn('text-xs', statusColors[call.status])}
                    >
                      {call.status}
                    </Badge>
                    {call.status === 'processing' && call.processing_step && (
                      <span className="text-xs text-muted-foreground">
                        {call.processing_step}
                      </span>
                    )}
                  </div>
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {call.source}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {call.duration_seconds ? formatDuration(call.duration_seconds) : '—'}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {formatDate(call.created_at)}
                </TableCell>
              </TableRow>
            ))}

            {!isLoading && calls.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-muted-foreground">
                  No calls found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page - 1)}
              disabled={page <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      <UploadCallDialog open={uploadOpen} onOpenChange={setUploadOpen} />
    </div>
  )
}
