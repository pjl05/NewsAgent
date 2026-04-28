import React, { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { GlassCard } from '../ui/GlassCard'
import { ContentItem } from '../../lib/api'
import { useTtsPlayer } from '../../contexts/TtsPlayerContext'
import { useAppStore } from '../../stores/appStore'

interface FeedCardProps {
  item: ContentItem
  index: number
}

export const FeedCard: React.FC<FeedCardProps> = ({ item, index }) => {
  const cardRef = useRef<HTMLDivElement>(null)
  const { play } = useTtsPlayer()
  const tts = useAppStore((s) => s.tts)

  useEffect(() => {
    if (!cardRef.current) return
    const ctx = gsap.context(() => {}, cardRef)
    gsap.from(cardRef.current, {
      y: 60,
      opacity: 0,
      scale: 0.95,
      duration: 0.6,
      delay: index * 0.1,
      ease: 'back.out(1.7)',
    })
    return () => ctx.revert()
  }, [index])

  const handlePlayTts = () => play(item.content_id, item.title)
  const isCurrentPlaying = tts.isPlaying && tts.currentContentId === item.content_id

  return (
    <div ref={cardRef}>
      <GlassCard aurora className="overflow-hidden">
        <div className="card-media relative h-44 overflow-hidden">
          {item.image_url ? (
            <img src={item.image_url} alt="" className="w-full h-full object-cover" loading="lazy" />
          ) : (
            <div className="absolute inset-0 bg-gradient-to-br from-aurora-purple/30 to-aurora-blue/30" />
          )}
          <span className="absolute top-3 left-3 px-2 py-0.5 rounded-full text-[10px] font-mono bg-black/40 text-text-secondary backdrop-blur-[8px]">
            {item.source}
          </span>
        </div>

        <div className="p-4">
          {item.tags && item.tags.length > 0 && (
            <div className="flex gap-2 mb-2">
              {item.tags.slice(0, 2).map((tag) => (
                <span key={tag} className="px-2 py-0.5 rounded-full text-[10px] bg-aurora-purple/20 text-aurora-cyan border border-aurora-purple/30">
                  {tag}
                </span>
              ))}
            </div>
          )}
          <h3 className="font-display font-bold text-base text-text-primary leading-snug mb-2 line-clamp-2">
            {item.title}
          </h3>
          <p className="font-body text-text-secondary text-sm leading-relaxed line-clamp-3">
            {item.summary}
          </p>
        </div>

        <div className="px-4 pb-4 flex items-center gap-3">
          <button
            onClick={handlePlayTts}
            className={[
              'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium',
              'transition-all duration-200 active:scale-95',
              isCurrentPlaying
                ? 'bg-aurora-purple text-white shadow-[0_4px_15px_rgba(99,102,241,0.5)]'
                : 'bg-white/[0.07] border border-white/[0.12] text-text-primary hover:bg-white/[0.12]',
            ].join(' ')}
          >
            🔊 {isCurrentPlaying ? '播放中' : '朗读'}
          </button>
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs bg-white/[0.07] border border-white/[0.12] text-text-primary transition-all duration-200 active:scale-95 hover:bg-white/[0.12]">
            ♥ {item.like_count ?? 0}
          </button>
        </div>
      </GlassCard>
    </div>
  )
}