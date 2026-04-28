import React, { useState, useCallback, useRef } from 'react'
import { GlassInput } from '../ui/GlassInput'
import { SearchResults } from './SearchResults'
import { useSearch } from '../../hooks/useApi'

const SEARCH_HISTORY_KEY = 'newsagent_search_history'
const MAX_HISTORY = 5

const getHistory = (): string[] => {
  try {
    return JSON.parse(localStorage.getItem(SEARCH_HISTORY_KEY) ?? '[]')
  } catch (e: unknown) {
    console.warn('Failed to parse search history:', e)
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

  const handleHistoryClick = useCallback((h: string) => { setQuery(h); search(h) }, [search])

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
