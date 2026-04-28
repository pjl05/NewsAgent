import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export interface ContentItem {
  content_id: string
  title: string
  summary: string
  source: string
  url: string
  image_url?: string
  tags?: string[]
  like_count?: number
  published_at?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export const api = {
  getRecommend: (userId?: string, topK = 20): Promise<{ results: ContentItem[], count?: number }> =>
    client.get('/content/recommend', { params: { user_id: userId ?? undefined, top_k: topK } }),

  searchContent: (query: string): Promise<{ results: ContentItem[] }> =>
    client.post('/content/search', { query }),

  generateTts: (contentId: string, voice?: string): Promise<{ audio_url: string }> =>
    client.post('/content/tts', { content_id: contentId, voice: voice ?? undefined }),

  summarize: (content: string): Promise<{ summary: string }> =>
    client.post('/content/summarize', { content }),

  query: (message: string): Promise<{ response: string }> =>
    client.post('/query', { message }),
}