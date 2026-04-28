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