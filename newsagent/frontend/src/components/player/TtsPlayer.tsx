import React from 'react'
import { useAppStore } from '../../stores/appStore'
import { useTtsPlayer } from '../../contexts/TtsPlayerContext'

const formatTime = (s: number) => {
  if (isNaN(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

export const TtsPlayer: React.FC = () => {
  const tts = useAppStore((s) => s.tts)
  const { toggle, close } = useTtsPlayer()

  const barHeights = React.useMemo(
    () => Array.from({ length: 5 }, () => 20 + Math.random() * 60),
    []
  )

  if (!tts.isPlaying && !tts.currentContentId) return null

  return (
    <div className="fixed bottom-[90px] left-4 right-4 z-[90] animate-[player-slide-up] rounded-2xl bg-[rgba(10,10,20,0.95)] backdrop-blur-[20px] border border-aurora-purple shadow-[0_0_40px_rgba(99,102,241,0.3)] p-4">
      <div className="flex items-center gap-4">
        <div className="flex-1 min-w-0">
          <p className="font-display font-medium text-sm text-text-primary truncate">
            {tts.currentTitle || '正在播放...'}
          </p>
          <p className="font-mono text-[11px] text-text-muted mt-0.5">
            {formatTime(tts.currentTime)} / {formatTime(tts.duration)}
          </p>
        </div>

        <div className="flex items-center gap-1 h-10">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="w-1 rounded-full bg-gradient-to-t from-aurora-purple to-aurora-cyan"
              style={{
                height: `${barHeights[i]}%`,
                animationDelay: `${i * 0.1}s`,
                animation: 'wave-rise 0.8s ease-in-out infinite alternate',
              }}
            />
          ))}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggle}
            aria-label={tts.isPlaying ? '暂停' : '继续'}
            className="w-10 h-10 rounded-full bg-aurora-purple/20 border border-aurora-purple/50 flex items-center justify-center text-lg hover:bg-aurora-purple/30 active:scale-95 transition-all focus-visible:ring-2 focus-visible:ring-aurora-purple focus-visible:ring-offset-2 focus-visible:ring-offset-[rgba(10,10,20,0.95)]"
          >
            {tts.isPlaying ? '⏸' : '▶'}
          </button>
          <button
            onClick={close}
            aria-label="关闭播放器"
            className="w-8 h-8 rounded-full bg-white/[0.07] border border-white/[0.12] flex items-center justify-center text-text-muted text-sm hover:bg-white/[0.12] active:scale-95 transition-all focus-visible:ring-2 focus-visible:ring-aurora-purple focus-visible:ring-offset-2 focus-visible:ring-offset-[rgba(10,10,20,0.95)]"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}