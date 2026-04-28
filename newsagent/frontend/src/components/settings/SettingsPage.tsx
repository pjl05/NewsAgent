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
