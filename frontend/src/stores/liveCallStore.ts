import { create } from 'zustand'
import type {
  TranscriptSegment,
  ChecklistProgress,
  ClientCardData,
  WSCoachingTip,
} from '@/types'

interface LiveCallState {
  callId: string | null
  isRecording: boolean
  currentStageId: string | null
  currentStageName: string | null
  transcript: TranscriptSegment[]
  checklistProgress: ChecklistProgress | null
  clientCardData: ClientCardData | null
  coachingTips: WSCoachingTip[]
  elapsedSeconds: number

  setCallId: (id: string | null) => void
  setRecording: (recording: boolean) => void
  setCurrentStage: (id: string, name: string) => void
  addTranscriptSegment: (segment: TranscriptSegment) => void
  setChecklistProgress: (progress: ChecklistProgress) => void
  updateChecklistItem: (
    stageId: string,
    itemId: string,
    completed: boolean,
    confidence: number,
    evidence: string
  ) => void
  setClientCardData: (data: ClientCardData) => void
  updateClientCardField: (
    fieldId: string,
    value: string,
    confidence: number,
    evidence: string
  ) => void
  addCoachingTip: (tip: WSCoachingTip) => void
  setElapsedSeconds: (seconds: number) => void
  reset: () => void
}

const initialState = {
  callId: null,
  isRecording: false,
  currentStageId: null,
  currentStageName: null,
  transcript: [],
  checklistProgress: null,
  clientCardData: null,
  coachingTips: [],
  elapsedSeconds: 0,
}

export const useLiveCallStore = create<LiveCallState>((set) => ({
  ...initialState,

  setCallId: (callId) => set({ callId }),
  setRecording: (isRecording) => set({ isRecording }),
  setCurrentStage: (id, name) =>
    set({ currentStageId: id, currentStageName: name }),

  addTranscriptSegment: (segment) =>
    set((state) => ({ transcript: [...state.transcript, segment] })),

  setChecklistProgress: (checklistProgress) => set({ checklistProgress }),

  updateChecklistItem: (stageId, itemId, completed, confidence, evidence) =>
    set((state) => {
      if (!state.checklistProgress) return state
      const stages = state.checklistProgress.stages.map((stage) => {
        if (stage.stage_id !== stageId) return stage
        return {
          ...stage,
          items: stage.items.map((item) => {
            if (item.item_id !== itemId) return item
            return {
              ...item,
              completed,
              confidence,
              evidence,
              completed_at: completed ? new Date().toISOString() : null,
            }
          }),
        }
      })
      return { checklistProgress: { stages } }
    }),

  setClientCardData: (clientCardData) => set({ clientCardData }),

  updateClientCardField: (fieldId, value, confidence, evidence) =>
    set((state) => ({
      clientCardData: {
        ...state.clientCardData,
        [fieldId]: {
          value,
          confidence,
          evidence,
          extracted_at: new Date().toISOString(),
        },
      },
    })),

  addCoachingTip: (tip) =>
    set((state) => ({ coachingTips: [...state.coachingTips, tip] })),

  setElapsedSeconds: (elapsedSeconds) => set({ elapsedSeconds }),
  reset: () => set(initialState),
}))
