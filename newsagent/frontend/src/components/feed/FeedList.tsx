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