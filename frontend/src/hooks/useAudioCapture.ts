import { useRef, useCallback } from 'react'

interface AudioCaptureOptions {
  onChunk: (chunk: ArrayBuffer) => void
  sampleRate?: number
  chunkSize?: number
}

export function useAudioCapture({ onChunk, sampleRate = 16000, chunkSize = 8192 }: AudioCaptureOptions) {
  const streamRef = useRef<MediaStream | null>(null)
  const cleanupRef = useRef<(() => void) | null>(null)

  const start = useCallback(async () => {
    // Request display capture with audio
    const stream = await navigator.mediaDevices.getDisplayMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 44100,
      },
      video: true, // Required for Chrome to allow audio capture
    })

    const audioTracks = stream.getAudioTracks()
    if (audioTracks.length === 0) {
      stream.getTracks().forEach((t) => t.stop())
      throw new Error('No audio track captured. Make sure to check "Share audio".')
    }

    streamRef.current = stream

    // Web Audio API — resample to 16kHz and convert to Int16 PCM
    const audioContext = new AudioContext({ sampleRate })
    const source = audioContext.createMediaStreamSource(stream)
    const processor = audioContext.createScriptProcessor(4096, 1, 1)

    let buffer = new Float32Array(0)

    processor.onaudioprocess = (e) => {
      const input = e.inputBuffer.getChannelData(0)
      const next = new Float32Array(buffer.length + input.length)
      next.set(buffer)
      next.set(input, buffer.length)
      buffer = next

      while (buffer.length >= chunkSize) {
        const slice = buffer.slice(0, chunkSize)
        buffer = buffer.slice(chunkSize)

        // Float32 → Int16
        const int16 = new Int16Array(slice.length)
        for (let i = 0; i < slice.length; i++) {
          int16[i] = slice[i] < 0 ? slice[i] * 0x8000 : slice[i] * 0x7fff
        }
        onChunk(int16.buffer)
      }
    }

    source.connect(processor)
    processor.connect(audioContext.destination)

    cleanupRef.current = () => {
      processor.disconnect()
      source.disconnect()
      audioContext.close()
    }

    // Return a handle for the audio track end event
    return {
      onTrackEnded: (cb: () => void) => {
        audioTracks[0].onended = cb
      },
    }
  }, [onChunk, sampleRate, chunkSize])

  const stop = useCallback(() => {
    cleanupRef.current?.()
    cleanupRef.current = null

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop())
      streamRef.current = null
    }
  }, [])

  return { start, stop }
}
