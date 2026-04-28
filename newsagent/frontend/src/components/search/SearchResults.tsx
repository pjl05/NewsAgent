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
        onClick={() => window.open(item.url, '_blank', 'noopener,noreferrer')}
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
