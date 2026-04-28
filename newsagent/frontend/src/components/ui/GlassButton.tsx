import React from 'react'

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  variant = 'ghost',
  size = 'md',
  className = '',
  ...props
}) => {
  const base = [
    'inline-flex items-center justify-center font-medium rounded-full',
    'transition-all duration-200 active:scale-95',
    variant === 'primary'
      ? 'bg-gradient-to-r from-aurora-purple to-aurora-blue text-white shadow-[0_4px_15px_rgba(99,102,241,0.4)]'
      : 'bg-white/[0.07] border border-white/[0.12] text-text-primary backdrop-blur-[12px]',
    size === 'sm' ? 'px-3 py-1.5 text-xs' : size === 'lg' ? 'px-6 py-3 text-base' : 'px-4 py-2 text-sm',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <button {...props} className={[base, className].filter(Boolean).join(' ')}>
      {children}
    </button>
  )
}