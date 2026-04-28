import { create } from 'zustand'

export type Tab = 'feed' | 'search' | 'chat' | 'settings'

interface TtsState {
  isPlaying: boolean
  currentContentId: string | null
  currentTitle: string
  currentTime: number
  duration: number
}

interface AppState {
  activeTab: Tab
  setActiveTab: (tab: Tab) => void
  tts: TtsState
  setTtsPlaying: (playing: boolean, contentId?: string, title?: string) => void
  setTtsTime: (currentTime: number, duration: number) => void
  userSubscriptions: string[]
  setUserSubscriptions: (topics: string[]) => void
  ttsVoice: string
  setTtsVoice: (voice: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'feed',
  setActiveTab: (tab) => set({ activeTab: tab }),

  tts: {
    isPlaying: false,
    currentContentId: null,
    currentTitle: '',
    currentTime: 0,
    duration: 0,
  },
  setTtsPlaying: (playing, contentId, title) =>
    set((state) => ({
      tts: {
        ...state.tts,
        isPlaying: playing,
        currentContentId: contentId ?? state.tts.currentContentId,
        currentTitle: title ?? state.tts.currentTitle,
      },
    })),
  setTtsTime: (currentTime, duration) =>
    set((state) => ({
      tts: { ...state.tts, currentTime, duration },
    })),

  userSubscriptions: ['AI', '科技', '投资'],
  setUserSubscriptions: (topics) => set({ userSubscriptions: topics }),
  ttsVoice: 'male-qn',
  setTtsVoice: (voice) => set({ ttsVoice: voice }),
}))
