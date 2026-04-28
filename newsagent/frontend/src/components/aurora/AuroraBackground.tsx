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
