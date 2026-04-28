# NewsAgent 前端实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `newsagent/frontend/` 目录下搭建完整的 React 移动端应用，包含 Aurora 极光背景、Glassmorphism UI 组件库、4 个 Tab 页面、TTS 播放器，对接后端 API。

**Architecture:** React 18 + Vite 单页应用，移动端优先（320-428px），Zustand 管理全局状态（当前 Tab、TTS 播放态、用户设置），GSAP 处理入场/交互动效，Axios 对接后端 `/api` 代理端点。

**Tech Stack:** React 18, Vite 5, TailwindCSS 3, GSAP 3, Zustand 4, Axios 1, TypeScript 5, React Router 6

---

## 文件结构

```
newsagent/frontend/
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── tsconfig.node.json
├── index.html
├── playwright.config.ts
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── components/
│   │   ├── aurora/
│   │   │   └── AuroraBackground.tsx
│   │   ├── ui/
│   │   │   ├── GlassCard.tsx
│   │   │   ├── GlassInput.tsx
│   │   │   ├── GlassNav.tsx
│   │   │   └── GlassButton.tsx
│   │   ├── feed/
│   │   │   ├── FeedPage.tsx
│   │   │   ├── FeedCard.tsx
│   │   │   └── FeedList.tsx
│   │   ├── search/
│   │   │   ├── SearchPage.tsx
│   │   │   └── SearchResults.tsx
│   │   ├── chat/
│   │   │   ├── ChatPage.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   └── ChatInput.tsx
│   │   ├── settings/
│   │   │   ├── SettingsPage.tsx
│   │   │   ├── TopicSelector.tsx
│   │   │   └── TtsSettings.tsx
│   │   └── player/
│   │       └── TtsPlayer.tsx
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useTtsPlayer.ts
│   │   └── useGsap.ts
│   ├── stores/
│   │   └── appStore.ts
│   └── lib/
│       └── api.ts
└── tests/
    └── e2e/
        └── main.spec.ts
```

---

## Task 0: 项目脚手架

**Files:**
- Create: `newsagent/frontend/package.json`
- Create: `newsagent/frontend/vite.config.ts`
- Create: `newsagent/frontend/tailwind.config.js`
- Create: `newsagent/frontend/postcss.config.js`
- Create: `newsagent/frontend/tsconfig.json`
- Create: `newsagent/frontend/tsconfig.node.json`
- Create: `newsagent/frontend/index.html`
- Create: `newsagent/frontend/src/main.tsx`
- Create: `newsagent/frontend/src/index.css`

---

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "newsagent-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "gsap": "^3.12.5",
    "zustand": "^4.5.2",
    "axios": "^1.7.2"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.5.2",
    "vite": "^5.3.1",
    "@playwright/test": "^1.44.1"
  }
}
```

- [ ] **Step 2: 创建 vite.config.ts**

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: 创建 tailwind.config.js**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'bg-deep': '#0a0a0f',
        'bg-surface': '#12121f',
        'bg-elevated': '#1a1a2e',
        'aurora-purple': '#6366f1',
        'aurora-blue': '#8b5cf6',
        'aurora-cyan': '#22d3ee',
        'accent-warm': '#f59e0b',
        'accent-rose': '#f43f5e',
        'text-primary': '#f1f5f9',
        'text-secondary': '#94a3b8',
        'text-muted': '#64748b',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'aurora-drift': 'aurora-drift 8s ease-in-out infinite alternate',
        'wave-rise': 'wave-rise 0.8s ease-in-out infinite alternate',
        'bubble-pop': 'bubble-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'player-slide-up': 'player-slide-up 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      keyframes: {
        'aurora-drift': {
          '0%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(30px, -40px) scale(1.05)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.95)' },
          '100%': { transform: 'translate(40px, 30px) scale(1.02)' },
        },
        'wave-rise': {
          '0%': { transform: 'scaleY(0.3)', opacity: '0.6' },
          '100%': { transform: 'scaleY(1)', opacity: '1' },
        },
        'bubble-pop': {
          '0%': { transform: 'scale(0.8)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'player-slide-up': {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 4: 创建 postcss.config.js**

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 5: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 6: 创建 tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 7: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
    <title>NewsAgent</title>
    <link
      href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 8: 创建 src/main.tsx**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 9: 创建 src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg-deep: #0a0a0f;
  --bg-surface: #12121f;
  --bg-elevated: #1a1a2e;
  --aurora-purple: #6366f1;
  --aurora-blue: #8b5cf6;
  --aurora-cyan: #22d3ee;
  --accent-warm: #f59e0b;
  --accent-rose: #f43f5e;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.12);
  --glass-glow: rgba(99, 102, 241, 0.3);
  --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 20px var(--glass-glow);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body,
#root {
  height: 100%;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--glass-border);
  border-radius: 2px;
}

.aurora-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
  overflow: hidden;
}

.aurora-blob-1 {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, #6366f1 0%, transparent 70%);
  top: -200px;
  left: -200px;
  opacity: 0.6;
  mix-blend-mode: screen;
  filter: blur(80px);
  animation: aurora-blob-1-drift 8s ease-in-out infinite alternate;
}

.aurora-blob-2 {
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, #8b5cf6 0%, transparent 70%);
  bottom: -150px;
  right: -150px;
  opacity: 0.6;
  mix-blend-mode: screen;
  filter: blur(80px);
  animation: aurora-blob-2-drift 12s ease-in-out infinite alternate;
  animation-delay: -4s;
}

.aurora-blob-3 {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, #22d3ee 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.3;
  mix-blend-mode: screen;
  filter: blur(80px);
  animation: aurora-blob-3-drift 18s ease-in-out infinite alternate;
  animation-delay: -8s;
}

@keyframes aurora-blob-1-drift {
  0%   { transform: translate(0, 0) scale(1); }
  33%  { transform: translate(30px, -40px) scale(1.05); }
  66%  { transform: translate(-20px, 20px) scale(0.95); }
  100% { transform: translate(40px, 30px) scale(1.02); }
}

@keyframes aurora-blob-2-drift {
  0%   { transform: translate(0, 0) scale(1); }
  50%  { transform: translate(-30px, 40px) scale(1.08); }
  100% { transform: translate(20px, -20px) scale(0.97); }
}

@keyframes aurora-blob-3-drift {
  0%   { transform: translate(-50%, -50%) scale(1); }
  40%  { transform: translate(-55%, -45%) scale(1.1); }
  70%  { transform: translate(-45%, -55%) scale(0.92); }
  100% { transform: translate(-52%, -48%) scale(1.05); }
}
```

---

## Task 1: 状态管理

**Files:**
- Create: `newsagent/frontend/src/stores/appStore.ts`

---

- [ ] **Step 1: 创建 appStore.ts (Zustand store)**

```ts
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
```

---

## Task 2: API 封装

**Files:**
- Create: `newsagent/frontend/src/lib/api.ts`

---

- [ ] **Step 1: 创建 api.ts**

```ts
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
  getRecommend: (userId?: string, topK = 20): Promise<{ data: ContentItem[] }> =>
    client.get('/content/recommend', { params: { user_id: userId, top_k: topK } }),

  searchContent: (query: string): Promise<{ data: ContentItem[] }> =>
    client.post('/content/search', { query }),

  generateTts: (contentId: string, voice?: string): Promise<{ audio_url: string }> =>
    client.post('/content/tts', { content_id: contentId, voice }),

  summarize: (content: string): Promise<{ summary: string }> =>
    client.post('/content/summarize', { content }),

  query: (message: string): Promise<{ response: string }> =>
    client.post('/query', { message }),
}
```

---

## Task 3: Aurora 极光背景组件

**Files:**
- Create: `newsagent/frontend/src/components/aurora/AuroraBackground.tsx`

---

- [ ] **Step 1: 创建 AuroraBackground.tsx**

```tsx
import React from 'react'

export const AuroraBackground: React.FC = () => {
  return (
    <div className="aurora-bg fixed inset-0 z-0 overflow-hidden pointer-events-none">
      <div className="aurora-blob-1" />
      <div className="aurora-blob-2" />
      <div className="aurora-blob-3" />
    </div>
  )
}
```

---

## Task 4: 玻璃拟态 UI 组件库

**Files:**
- Create: `newsagent/frontend/src/components/ui/GlassCard.tsx`
- Create: `newsagent/frontend/src/components/ui/GlassInput.tsx`
- Create: `newsagent/frontend/src/components/ui/GlassNav.tsx`
- Create: `newsagent/frontend/src/components/ui/GlassButton.tsx`

---

- [ ] **Step 1: 创建 GlassCard.tsx**

```tsx
import React from 'react'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  aurora?: boolean
  onClick?: () => void
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  aurora = false,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={[
        'bg-white/[0.05] backdrop-blur-[16px] border border-white/[0.12]',
        'rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.4)]',
        'transition-all duration-300 ease-out',
        'hover:shadow-[0_8px_32px_rgba(0,0,0,0.4),0_0_0_1px_#6366f1,0_0_30px_rgba(99,102,241,0.4)]',
        'hover:translate-y-[-2px] hover:scale-[1.01]',
        aurora ? 'hover:shadow-[0_8px_32px_rgba(0,0,0,0.4),0_0_0_1px_#6366f1,0_0_30px_rgba(99,102,241,0.4)]' : '',
        onClick ? 'cursor-pointer' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </div>
  )
}
```

- [ ] **Step 2: 创建 GlassInput.tsx**

```tsx
import React from 'react'

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode
}

export const GlassInput: React.FC<GlassInputProps> = ({
  icon,
  className = '',
  ...props
}) => {
  return (
    <div className="relative">
      {icon && (
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted">
          {icon}
        </span>
      )}
      <input
        {...props}
        className={[
          'w-full bg-white/[0.07] backdrop-blur-[12px] border border-white/[0.12]',
          'rounded-full py-3.5 px-5 text-text-primary font-body text-[15px]',
          'outline-none transition-all duration-200',
          'placeholder:text-text-muted',
          'focus:border-aurora-purple focus:shadow-[0_0_0_3px_rgba(99,102,241,0.2)]',
          icon ? 'pl-11' : '',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
      />
    </div>
  )
}
```

- [ ] **Step 3: 创建 GlassNav.tsx**

```tsx
import React from 'react'
import { Tab, useAppStore } from '../../stores/appStore'

const NAV_ITEMS: { tab: Tab; label: string; icon: string }[] = [
  { tab: 'feed', label: '精选', icon: '📰' },
  { tab: 'search', label: '搜索', icon: '🔍' },
  { tab: 'chat', label: 'AI', icon: '🤖' },
  { tab: 'settings', label: '设置', icon: '⚙️' },
]

export const GlassNav: React.FC = () => {
  const { activeTab, setActiveTab } = useAppStore()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-[100] h-[72px] bg-[rgba(10,10,15,0.8)] backdrop-blur-[20px] border-t border-white/[0.12] flex justify-around items-center pb-[env(safe-area-inset-bottom)]">
      {NAV_ITEMS.map(({ tab, label, icon }) => (
        <button
          key={tab}
          onClick={() => setActiveTab(tab)}
          className={[
            'flex flex-col items-center gap-1 transition-all duration-200',
            'text-text-muted text-[10px] font-medium',
            activeTab === tab
              ? 'text-text-primary scale-110'
              : 'hover:text-text-secondary active:scale-95',
          ].join(' ')}
        >
          <span className="text-xl">{icon}</span>
          <span>{label}</span>
        </button>
      ))}
    </nav>
  )
}
```

- [ ] **Step 4: 创建 GlassButton.tsx**

```tsx
import React from 'react'

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  variant = 'ghost',
  size = 'md',
  className = '',
  ...props
}) => {
  const base = [
    'inline-flex items-center justify-center font-medium rounded-full',
    'transition-all duration-200 active:scale-95',
    variant === 'primary'
      ? 'bg-gradient-to-r from-aurora-purple to-aurora-blue text-white shadow-[0_4px_15px_rgba(99,102,241,0.4)]'
      : 'bg-white/[0.07] border border-white/[0.12] text-text-primary backdrop-blur-[12px]',
    size === 'sm' ? 'px-3 py-1.5 text-xs' : size === 'lg' ? 'px-6 py-3 text-base' : 'px-4 py-2 text-sm',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <button {...props} className={[base, className].filter(Boolean).join(' ')}>
      {children}
    </button>
  )
}
```

---

## Task 5: App 根组件

**Files:**
- Create: `newsagent/frontend/src/App.tsx`

---

- [ ] **Step 1: 创建 App.tsx**

```tsx
import React from 'react'
import { AuroraBackground } from './components/aurora/AuroraBackground'
import { GlassNav } from './components/ui/GlassNav'
import { FeedPage } from './components/feed/FeedPage'
import { SearchPage } from './components/search/SearchPage'
import { ChatPage } from './components/chat/ChatPage'
import { SettingsPage } from './components/settings/SettingsPage'
import { TtsPlayer } from './components/player/TtsPlayer'
import { useAppStore } from './stores/appStore'

const PAGE_MAP = {
  feed: FeedPage,
  search: SearchPage,
  chat: ChatPage,
  settings: SettingsPage,
}

export default function App() {
  const activeTab = useAppStore((s) => s.activeTab)
  const ActivePage = PAGE_MAP[activeTab]

  return (
    <div className="relative min-h-screen bg-bg-deep">
      <AuroraBackground />
      <div className="relative z-10 min-h-screen pb-[100px]">
        <ActivePage />
      </div>
      <GlassNav />
      <TtsPlayer />
    </div>
  )
}
```

---

## Task 6: Hooks

**Files:**
- Create: `newsagent/frontend/src/hooks/useApi.ts`
- Create: `newsagent/frontend/src/hooks/useTtsPlayer.ts`
- Create: `newsagent/frontend/src/hooks/useGsap.ts`

---

- [ ] **Step 1: 创建 useApi.ts**

```ts
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
      setContents(res.data ?? [])
    } catch (e: any) {
      setError(e?.message ?? '获取推荐失败')
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
      setResults(res.data ?? [])
    } catch (e: any) {
      setError(e?.message ?? '搜索失败')
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
    } catch {
      const errMsg: ChatMessage = { role: 'assistant', content: '抱歉，出了点问题。' }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }, [])

  return { messages, loading, send }
}
```

- [ ] **Step 2: 创建 useTtsPlayer.ts**

```ts
import { useRef, useCallback } from 'react'
import { useAppStore } from '../stores/appStore'
import { api } from '../lib/api'

export function useTtsPlayer() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const { setTtsPlaying, setTtsTime } = useAppStore()

  const play = useCallback(
    async (contentId: string, title: string) => {
      if (audioRef.current) {
        audioRef.current.pause()
      }
      try {
        const res = await api.generateTts(contentId)
        const audio = new Audio(res.audio_url)
        audioRef.current = audio
        setTtsPlaying(true, contentId, title)

        audio.ontimeupdate = () => {
          setTtsTime(audio.currentTime, audio.duration)
        }
        audio.onended = () => setTtsPlaying(false)
        audio.onerror = () => setTtsPlaying(false)
        await audio.play()
      } catch {
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
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setTtsPlaying(false)
  }, [setTtsPlaying])

  return { play, toggle, close }
}
```

- [ ] **Step 3: 创建 useGsap.ts**

```ts
import { useEffect, useRef } from 'react'
import gsap from 'gsap'

export function useGsap() {
  const ctxRef = useRef<gsap.Context | null>(null)

  useEffect(() => {
    ctxRef.current = gsap.context(() => {})
    return () => ctxRef.current?.revert()
  }, [])

  const staggerCards = (selector: string) => {
    ctxRef.current?.add(() => {
      gsap.from(selector, {
        y: 60,
        opacity: 0,
        scale: 0.95,
        duration: 0.6,
        stagger: 0.1,
        ease: 'back.out(1.7)',
      })
    })
  }

  return { staggerCards }
}
```

---

## Task 7: Feed 页面（精选）

**Files:**
- Create: `newsagent/frontend/src/components/feed/FeedPage.tsx`
- Create: `newsagent/frontend/src/components/feed/FeedCard.tsx`
- Create: `newsagent/frontend/src/components/feed/FeedList.tsx`

---

- [ ] **Step 1: 创建 FeedCard.tsx**

```tsx
import React, { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { GlassCard } from '../ui/GlassCard'
import { ContentItem } from '../../lib/api'
import { useTtsPlayer } from '../../hooks/useTtsPlayer'
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
    gsap.from(cardRef.current, {
      y: 60,
      opacity: 0,
      scale: 0.95,
      duration: 0.6,
      delay: index * 0.1,
      ease: 'back.out(1.7)',
    })
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
```

- [ ] **Step 2: 创建 FeedList.tsx**

```tsx
import React from 'react'
import { FeedCard } from './FeedCard'
import { ContentItem } from '../../lib/api'

interface FeedListProps {
  contents: ContentItem[]
}

export const FeedList: React.FC<FeedListProps> = ({ contents }) => (
  <div className="px-4 pt-4 flex flex-col gap-4">
    {contents.map((item, index) => (
      <FeedCard key={item.content_id} item={item} index={index} />
    ))}
  </div>
)
```

- [ ] **Step 3: 创建 FeedPage.tsx**

```tsx
import React, { useEffect } from 'react'
import { FeedList } from './FeedList'
import { useRecommend } from '../../hooks/useApi'

export const FeedPage: React.FC = () => {
  const { loading, contents, error, fetchRecommend } = useRecommend()

  useEffect(() => { fetchRecommend() }, [fetchRecommend])

  return (
    <div className="min-h-screen px-4 pt-6">
      <header className="mb-6">
        <h1 className="font-display font-bold text-2xl text-text-primary">精选</h1>
        <p className="font-body text-text-muted text-sm mt-1">为你推荐最新内容</p>
      </header>

      {loading && (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-2 border-aurora-purple border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      {error && <div className="text-center py-20 text-accent-rose text-sm">{error}</div>}
      {!loading && !error && contents.length === 0 && (
        <div className="text-center py-20 text-text-muted text-sm">暂无推荐内容</div>
      )}
      {!loading && contents.length > 0 && <FeedList contents={contents} />}
    </div>
  )
}
```

---

## Task 8: Search 页面

**Files:**
- Create: `newsagent/frontend/src/components/search/SearchPage.tsx`
- Create: `newsagent/frontend/src/components/search/SearchResults.tsx`

---

- [ ] **Step 1: 创建 SearchPage.tsx**

```tsx
import React, { useState, useCallback, useRef } from 'react'
import { GlassInput } from '../ui/GlassInput'
import { SearchResults } from './SearchResults'
import { useSearch } from '../../hooks/useApi'

const SEARCH_HISTORY_KEY = 'newsagent_search_history'
const MAX_HISTORY = 5

const getHistory = (): string[] => {
  try {
    return JSON.parse(localStorage.getItem(SEARCH_HISTORY_KEY) ?? '[]')
  } catch {
    return []
  }
}

const addToHistory = (query: string) => {
  const prev = getHistory().filter((h) => h !== query)
  localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify([query, ...prev].slice(0, MAX_HISTORY)))
}

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState<string[]>(getHistory)
  const { loading, results, error, search } = useSearch()
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value
      setQuery(val)
      if (debounceRef.current) clearTimeout(debounceRef.current)
      debounceRef.current = setTimeout(() => search(val), 400)
    },
    [search]
  )

  const handleHistoryClick = (h: string) => { setQuery(h); search(h) }

  const handleSearch = () => {
    if (!query.trim()) return
    addToHistory(query)
    setHistory(getHistory())
    search(query)
  }

  return (
    <div className="min-h-screen px-4 pt-6">
      <header className="mb-6">
        <h1 className="font-display font-bold text-2xl text-text-primary">搜索</h1>
      </header>

      <div className="mb-6">
        <GlassInput
          placeholder="搜索内容..."
          value={query}
          onChange={handleChange}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          icon={<span>🔍</span>}
        />
      </div>

      {!query && history.length > 0 && (
        <div className="mb-6">
          <h4 className="font-body text-text-muted text-xs mb-3 uppercase tracking-wider">最近搜索</h4>
          <div className="flex flex-wrap gap-2">
            {history.map((h) => (
              <button
                key={h}
                onClick={() => handleHistoryClick(h)}
                className="px-3 py-1.5 rounded-full text-xs bg-white/[0.07] border border-white/[0.12] text-text-secondary backdrop-blur-[8px] hover:bg-white/[0.12] hover:text-text-primary transition-all active:scale-95"
              >
                {h}
              </button>
            ))}
          </div>
        </div>
      )}

      {loading && <div className="flex justify-center py-16"><div className="w-8 h-8 border-2 border-aurora-purple border-t-transparent rounded-full animate-spin" /></div>}
      {error && <div className="text-center py-16 text-accent-rose text-sm">{error}</div>}
      {query && !loading && results.length > 0 && <SearchResults results={results} />}
      {query && !loading && results.length === 0 && <div className="text-center py-16 text-text-muted text-sm">没有找到相关结果</div>}
    </div>
  )
}
```

- [ ] **Step 2: 创建 SearchResults.tsx**

```tsx
import React from 'react'
import { GlassCard } from '../ui/GlassCard'
import { ContentItem } from '../../lib/api'

interface SearchResultsProps {
  results: ContentItem[]
}

export const SearchResults: React.FC<SearchResultsProps> = ({ results }) => (
  <div className="flex flex-col gap-3">
    {results.map((item) => (
      <GlassCard
        key={item.content_id}
        className="p-4"
        onClick={() => window.open(item.url, '_blank')}
      >
        <div className="flex items-start gap-3">
          {item.image_url && (
            <img src={item.image_url} alt="" className="w-16 h-16 rounded-lg object-cover flex-shrink-0" loading="lazy" />
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-display font-bold text-sm text-text-primary line-clamp-2 mb-1">{item.title}</h3>
            <p className="font-body text-text-muted text-xs line-clamp-2">{item.summary}</p>
            <span className="inline-block mt-1.5 text-[10px] text-text-muted font-mono">{item.source}</span>
          </div>
        </div>
      </GlassCard>
    ))}
  </div>
)
```

---

## Task 9: Chat 页面

**Files:**
- Create: `newsagent/frontend/src/components/chat/ChatPage.tsx`
- Create: `newsagent/frontend/src/components/chat/ChatMessage.tsx`
- Create: `newsagent/frontend/src/components/chat/ChatInput.tsx`

---

- [ ] **Step 1: 创建 ChatMessage.tsx**

```tsx
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
```

- [ ] **Step 2: 创建 ChatInput.tsx**

```tsx
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
```

- [ ] **Step 3: 创建 ChatPage.tsx**

```tsx
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
```

---

## Task 10: Settings 页面

**Files:**
- Create: `newsagent/frontend/src/components/settings/SettingsPage.tsx`
- Create: `newsagent/frontend/src/components/settings/TopicSelector.tsx`
- Create: `newsagent/frontend/src/components/settings/TtsSettings.tsx`

---

- [ ] **Step 1: 创建 TopicSelector.tsx**

```tsx
import React from 'react'
import { useAppStore } from '../../stores/appStore'

const ALL_TOPICS = ['AI', '科技', '投资', '创业', '国际', '社会', '文化', '体育']

export const TopicSelector: React.FC = () => {
  const { userSubscriptions, setUserSubscriptions } = useAppStore()

  const toggle = (topic: string) => {
    if (userSubscriptions.includes(topic)) {
      setUserSubscriptions(userSubscriptions.filter((t) => t !== topic))
    } else {
      setUserSubscriptions([...userSubscriptions, topic])
    }
  }

  return (
    <div>
      <h4 className="font-body text-text-muted text-xs mb-3 uppercase tracking-wider">订阅主题</h4>
      <div className="flex flex-wrap gap-2">
        {ALL_TOPICS.map((topic) => {
          const active = userSubscriptions.includes(topic)
          return (
            <button
              key={topic}
              onClick={() => toggle(topic)}
              className={[
                'px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
                active
                  ? 'bg-gradient-to-r from-aurora-purple to-aurora-blue text-white shadow-[0_4px_15px_rgba(99,102,241,0.4)] border-transparent'
                  : 'bg-white/[0.07] border border-white/[0.12] text-text-secondary hover:bg-white/[0.12] hover:text-text-primary',
              ].join(' ')}
            >
              {topic}
            </button>
          )
        })}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 创建 TtsSettings.tsx**

```tsx
import React from 'react'
import { useAppStore } from '../../stores/appStore'

const VOICES = [
  { value: 'male-qn', label: '磁性男声' },
  { value: 'female-qn', label: '温柔女声' },
]

export const TtsSettings: React.FC = () => {
  const { ttsVoice, setTtsVoice } = useAppStore()

  return (
    <div>
      <h4 className="font-body text-text-muted text-xs mb-3 uppercase tracking-wider">语音设置</h4>
      <div className="flex flex-col gap-2">
        {VOICES.map((v) => (
          <button
            key={v.value}
            onClick={() => setTtsVoice(v.value)}
            className={[
              'flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all duration-200',
              ttsVoice === v.value
                ? 'bg-aurora-purple/20 border border-aurora-purple text-text-primary'
                : 'bg-white/[0.05] border border-white/[0.08] text-text-secondary hover:bg-white/[0.08]',
            ].join(' ')}
          >
            <span
              className={[
                'w-4 h-4 rounded-full border-2 flex items-center justify-center',
                ttsVoice === v.value ? 'border-aurora-purple' : 'border-text-muted',
              ].join(' ')}
            >
              {ttsVoice === v.value && <span className="w-2 h-2 rounded-full bg-aurora-purple" />}
            </span>
            {v.label}
          </button>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: 创建 SettingsPage.tsx**

```tsx
import React from 'react'
import { GlassCard } from '../ui/GlassCard'
import { TopicSelector } from './TopicSelector'
import { TtsSettings } from './TtsSettings'

export const SettingsPage: React.FC = () => (
  <div className="min-h-screen px-4 pt-6 pb-8">
    <header className="mb-6">
      <h1 className="font-display font-bold text-2xl text-text-primary">设置</h1>
    </header>

    <div className="flex flex-col gap-4">
      <GlassCard className="p-5"><TopicSelector /></GlassCard>
      <GlassCard className="p-5"><TtsSettings /></GlassCard>
      <GlassCard className="p-5">
        <h4 className="font-body text-text-muted text-xs mb-3 uppercase tracking-wider">关于</h4>
        <div className="text-text-secondary text-sm space-y-1">
          <p>NewsAgent v0.1.0</p>
          <p className="text-text-muted text-xs">自动化新闻采集与个性化推送平台</p>
        </div>
      </GlassCard>
    </div>
  </div>
)
```

---

## Task 11: TTS 播放器

**Files:**
- Create: `newsagent/frontend/src/components/player/TtsPlayer.tsx`

---

- [ ] **Step 1: 创建 TtsPlayer.tsx**

```tsx
import React from 'react'
import { useAppStore } from '../../stores/appStore'
import { useTtsPlayer } from '../../hooks/useTtsPlayer'

const formatTime = (s: number) => {
  if (isNaN(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

export const TtsPlayer: React.FC = () => {
  const tts = useAppStore((s) => s.tts)
  const { toggle, close } = useTtsPlayer()

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
                height: `${20 + Math.random() * 60}%`,
                animationDelay: `${i * 0.1}s`,
                animation: 'wave-rise 0.8s ease-in-out infinite alternate',
              }}
            />
          ))}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggle}
            className="w-10 h-10 rounded-full bg-aurora-purple/20 border border-aurora-purple/50 flex items-center justify-center text-lg hover:bg-aurora-purple/30 active:scale-95 transition-all"
          >
            {tts.isPlaying ? '⏸' : '▶'}
          </button>
          <button
            onClick={close}
            className="w-8 h-8 rounded-full bg-white/[0.07] border border-white/[0.12] flex items-center justify-center text-text-muted text-sm hover:bg-white/[0.12] active:scale-95 transition-all"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}
```

---

## Task 12: Playwright E2E 测试

**Files:**
- Create: `newsagent/frontend/playwright.config.ts`
- Create: `newsagent/frontend/tests/e2e/main.spec.ts`

---

- [ ] **Step 1: 创建 playwright.config.ts**

```ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

- [ ] **Step 2: 创建 tests/e2e/main.spec.ts**

```ts
import { test, expect } from '@playwright/test'

test('首页加载并显示精选标题', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toContainText('精选')
})

test('底部导航栏显示 4 个 Tab', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('精选')).toBeVisible()
  await expect(page.getByText('搜索')).toBeVisible()
  await expect(page.getByText('AI')).toBeVisible()
  await expect(page.getByText('设置')).toBeVisible()
})

test('点击搜索 Tab 切换到搜索页面', async ({ page }) => {
  await page.goto('/')
  await page.getByText('搜索').click()
  await expect(page.locator('h1')).toContainText('搜索')
})

test('点击 AI Tab 切换到 AI 对话页面', async ({ page }) => {
  await page.goto('/')
  await page.getByText('AI').click()
  await expect(page.locator('h1')).toContainText('AI 助手')
})

test('点击设置 Tab 切换到设置页面', async ({ page }) => {
  await page.goto('/')
  await page.getByText('设置').click()
  await expect(page.locator('h1')).toContainText('设置')
})
```

---

## 自检清单

**Spec 覆盖检查：**
- [x] Aurora 极光背景 → Task 3
- [x] 玻璃拟态 UI 组件（GlassCard/GlassInput/GlassNav/GlassButton） → Task 4
- [x] Tab 1 精选 Feed → Task 7
- [x] Tab 2 搜索 Search → Task 8
- [x] Tab 3 AI 对话 Chat → Task 9
- [x] Tab 4 个人设置 Settings → Task 10
- [x] TTS 声浪播放器 → Task 11
- [x] GSAP 动效（卡片弹入、气泡弹出） → Task 5, 7, 9
- [x] API 对接 → Task 2, 6
- [x] Zustand 状态管理 → Task 1
- [x] Tailscale/Vite 代理配置 → Task 0
- [x] E2E 测试 → Task 12

**占位符扫描：**
- 无 "TBD"、"TODO"、"fill in details"
- 无 "implement later"
- 所有代码块均包含完整实现

**类型一致性：**
- `api.ts` 中 `ContentItem`、`ChatMessage` 接口定义 → 被所有页面引用
- `useAppStore` 中 `Tab` 类型 → 被 `GlassNav` 和 `App` 引用
- `useTtsPlayer` 使用 `useAppStore` 的 tts 状态 → 类型匹配
