import React, { useEffect, useRef } from 'react'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { useChat } from '../../hooks/useApi'

export const ChatPage: React.FC = () => {
  const { messages, loading, send } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="min-h-screen flex flex-col">
      <header className="px-4 pt-6 pb-4">
        <h1 className="font-display font-bold text-2xl text-text-primary">AI 助手</h1>
        <p className="font-body text-text-muted text-sm mt-0.5">有问题尽管问我</p>
      </header>

      <div className="flex-1 overflow-y-auto px-4 pb-4 flex flex-col gap-3">
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center text-text-muted text-sm gap-3 py-20">
            <span className="text-4xl">🤖</span>
            <p>我是你的 AI 助手，可以帮你解答问题或聊天</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} index={i} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="px-4 pb-4 pt-2 border-t border-white/[0.06]">
        <ChatInput onSend={send} loading={loading} />
      </div>
    </div>
  )
}
