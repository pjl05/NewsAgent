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
