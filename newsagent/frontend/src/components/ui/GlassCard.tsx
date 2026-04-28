import React from 'react'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  aurora?: boolean
  onClick?: () => void
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  aurora = false,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={[
        'bg-white/[0.05] backdrop-blur-[16px] border border-white/[0.12]',
        'rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.4)]',
        'transition-all duration-300 ease-out',
        'hover:shadow-[0_8px_32px_rgba(0,0,0,0.4),0_0_0_1px_#6366f1,0_0_30px_rgba(99,102,241,0.4)]',
        'hover:translate-y-[-2px] hover:scale-[1.01]',
        aurora ? 'hover:shadow-[0_8px_32px_rgba(0,0,0,0.4),0_0_0_1px_#6366f1,0_0_30px_rgba(99,102,241,0.4)]' : '',
        onClick ? 'cursor-pointer' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </div>
  )
}