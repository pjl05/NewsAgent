import { AuroraBackground } from './components/aurora/AuroraBackground'
import { GlassNav } from './components/ui/GlassNav'
import { FeedPage } from './components/feed/FeedPage'
import { SearchPage } from './components/search/SearchPage'
import { ChatPage } from './components/chat/ChatPage'
import { SettingsPage } from './components/settings/SettingsPage'
import { TtsPlayer } from './components/player/TtsPlayer'
import { TtsPlayerProvider } from './contexts/TtsPlayerContext'
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
    <TtsPlayerProvider>
      <div className="relative min-h-screen bg-bg-deep">
        <AuroraBackground />
        <div className="relative z-10 min-h-screen pb-[100px]">
          <ActivePage />
        </div>
        <GlassNav />
        <TtsPlayer />
      </div>
    </TtsPlayerProvider>
  )
}