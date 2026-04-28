import React, { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ChatMessage as ChatMessageType } from '../../lib/api'

interface ChatMessageProps {
  message: ChatMessageType
  index: number
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, index }) => {
  const bubbleRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!bubbleRef.current) return
    gsap.from(bubbleRef.current, {
      scale: 0.8,
      opacity: 0,
      duration: 0.4,
      delay: index * 0.05,
      ease: 'back.out(1.7)',
    })
  }, [index])

  const isUser = message.role === 'user'

  return (
    <div className={['flex', isUser ? 'justify-end' : 'justify-start'].join(' ')}>
      <div
        ref={bubbleRef}
        className={[
          'max-w-[80%] px-4 py-3 text-sm leading-relaxed',
          isUser
            ? 'bg-gradient-to-r from-aurora-purple to-aurora-blue text-white rounded-[20px_20px_4px_20px]'
            : 'bg-white/[0.05] border border-white/[0.12] text-text-primary backdrop-blur-[12px] rounded-[20px_20px_20px_4px]',
        ].join(' ')}
      >
        {message.content}
      </div>
    </div>
  )
}
