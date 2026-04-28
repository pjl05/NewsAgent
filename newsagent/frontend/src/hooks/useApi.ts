import { useState, useCallback } from 'react'
import { api, ContentItem, ChatMessage } from '../lib/api'

export function useRecommend() {
  const [loading, setLoading] = useState(false)
  const [contents, setContents] = useState<ContentItem[]>([])
  const [error, setError] = useState<string | null>(null)

  const fetchRecommend = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.getRecommend()
      setContents(res.results ?? [])
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : '获取推荐失败'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { loading, contents, error, fetchRecommend }
}

export function useSearch() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<ContentItem[]>([])
  const [error, setError] = useState<string | null>(null)

  const search = useCallback(async (query: string) => {
    if (!query.trim()) {
      setResults([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await api.searchContent(query)
      setResults(res.results ?? [])
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : '搜索失败'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { loading, results, error, search }
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)

  const send = useCallback(async (text: string) => {
    const userMsg: ChatMessage = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    try {
      const res = await api.query(text)
      const assistantMsg: ChatMessage = { role: 'assistant', content: res.response }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (e: unknown) {
      console.error('Chat send failed:', e)
      const errMsg: ChatMessage = { role: 'assistant', content: '抱歉，出了点问题。' }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }, [])

  return { messages, loading, send }
}
