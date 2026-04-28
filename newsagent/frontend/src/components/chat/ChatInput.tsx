import React, { useState } from 'react'
import { GlassInput } from '../ui/GlassInput'
import { GlassButton } from '../ui/GlassButton'

interface ChatInputProps {
  onSend: (text: string) => void
  loading: boolean
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, loading }) => {
  const [text, setText] = useState('')

  const handleSend = () => {
    if (!text.trim() || loading) return
    onSend(text.trim())
    setText('')
  }

  return (
    <div className="flex items-center gap-3">
      <GlassInput
        placeholder="输入消息..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        className="flex-1"
        disabled={loading}
      />
      <GlassButton
        variant="primary"
        onClick={handleSend}
        disabled={!text.trim() || loading}
        className="px-4 py-3 flex-shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? (
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : (
          '➤'
        )}
      </GlassButton>
    </div>
  )
}
