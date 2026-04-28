import React, { createContext, useContext, useRef, useCallback, useEffect } from 'react'
import { useAppStore } from '../stores/appStore'
import { api } from '../lib/api'

interface TtsPlayerContextValue {
  play: (contentId: string, title: string) => Promise<void>
  toggle: () => void
  close: () => void
}

const TtsPlayerContext = createContext<TtsPlayerContextValue | null>(null)

export function TtsPlayerProvider({ children }: { children: React.ReactNode }) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const { setTtsPlaying, setTtsTime } = useAppStore()

  const play = useCallback(
    async (contentId: string, title: string) => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.src = ''
        audioRef.current = null
      }
      try {
        const res = await api.generateTts(contentId)
        const audio = new Audio(res.audio_url)
        audioRef.current = audio
        setTtsPlaying(true, contentId, title)

        audio.ontimeupdate = () => setTtsTime(audio.currentTime, audio.duration)
        audio.onended = () => setTtsPlaying(false)
        audio.onerror = () => setTtsPlaying(false)
        await audio.play()
      } catch (e: unknown) {
        console.error('TTS play failed:', e)
        setTtsPlaying(false)
      }
    },
    [setTtsPlaying, setTtsTime]
  )

  const toggle = useCallback(() => {
    const audio = audioRef.current
    if (!audio) return
    if (audio.paused) {
      audio.play()
    } else {
      audio.pause()
    }
  }, [])

  const close = useCallback(() => {
    const audio = audioRef.current
    if (audio) {
      audio.ontimeupdate = null
      audio.onended = null
      audio.onerror = null
      audio.pause()
      audio.src = ''
      audioRef.current = null
    }
    setTtsPlaying(false)
  }, [setTtsPlaying])

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.ontimeupdate = null
        audioRef.current.onended = null
        audioRef.current.onerror = null
        audioRef.current.pause()
        audioRef.current.src = ''
        audioRef.current = null
      }
    }
  }, [])

  return (
    <TtsPlayerContext.Provider value={{ play, toggle, close }}>
      {children}
    </TtsPlayerContext.Provider>
  )
}

export function useTtsPlayer(): TtsPlayerContextValue {
  const ctx = useContext(TtsPlayerContext)
  if (!ctx) throw new Error('useTtsPlayer must be used inside TtsPlayerProvider')
  return ctx
}