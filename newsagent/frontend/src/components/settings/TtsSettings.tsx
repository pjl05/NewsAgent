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
