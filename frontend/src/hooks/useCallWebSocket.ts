import { useRef, useCallback, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import type { WSCoachMessage } from '@/types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

interface UseCallWebSocketOptions {
  callId: string | null
  onMessage: (msg: WSCoachMessage) => void
  onStatusChange?: (status: 'connecting' | 'connected' | 'disconnected' | 'error') => void
}

export function useCallWebSocket({ callId, onMessage, onStatusChange }: UseCallWebSocketOptions) {
  const ingestRef = useRef<WebSocket | null>(null)
  const coachRef = useRef<WebSocket | null>(null)

  const connect = useCallback(async () => {
    if (!callId) return

    onStatusChange?.('connecting')

    // Get JWT for auth
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token || ''

    // Ingest WebSocket — sends audio
    const ingestWs = new WebSocket(`${WS_URL}/ws/call/${callId}/ingest?token=${token}`)
    ingestWs.onopen = () => console.log('[ws] ingest connected')
    ingestWs.onerror = () => console.error('[ws] ingest error')
    ingestWs.onclose = () => console.log('[ws] ingest closed')
    ingestRef.current = ingestWs

    // Coach WebSocket — receives real-time updates
    const coachWs = new WebSocket(`${WS_URL}/ws/call/${callId}/coach?token=${token}`)
    coachWs.onopen = () => {
      console.log('[ws] coach connected')
      onStatusChange?.('connected')
    }
    coachWs.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data) as WSCoachMessage
        onMessage(msg)
      } catch (err) {
        console.error('[ws] parse error:', err)
      }
    }
    coachWs.onerror = () => {
      console.error('[ws] coach error')
      onStatusChange?.('error')
    }
    coachWs.onclose = () => {
      console.log('[ws] coach closed')
      onStatusChange?.('disconnected')
    }
    coachRef.current = coachWs
  }, [callId, onMessage, onStatusChange])

  const disconnect = useCallback(() => {
    if (ingestRef.current) {
      ingestRef.current.close()
      ingestRef.current = null
    }
    if (coachRef.current) {
      coachRef.current.close()
      coachRef.current = null
    }
    onStatusChange?.('disconnected')
  }, [onStatusChange])

  const sendAudio = useCallback((chunk: ArrayBuffer) => {
    if (ingestRef.current?.readyState === WebSocket.OPEN) {
      ingestRef.current.send(chunk)
    }
  }, [])

  const sendCommand = useCallback((command: Record<string, unknown>) => {
    if (coachRef.current?.readyState === WebSocket.OPEN) {
      coachRef.current.send(JSON.stringify(command))
    }
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => disconnect()
  }, [disconnect])

  return { connect, disconnect, sendAudio, sendCommand }
}
