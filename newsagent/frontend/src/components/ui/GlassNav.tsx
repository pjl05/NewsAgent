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