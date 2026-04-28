import React from 'react'

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode
}

export const GlassInput: React.FC<GlassInputProps> = ({
  icon,
  className = '',
  ...props
}) => {
  return (
    <div className="relative">
      {icon && (
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted">
          {icon}
        </span>
      )}
      <input
        {...props}
        className={[
          'w-full bg-white/[0.07] backdrop-blur-[12px] border border-white/[0.12]',
          'rounded-full py-3.5 px-5 text-text-primary font-body text-[15px]',
          'outline-none transition-all duration-200',
          'placeholder:text-text-muted',
          'focus:border-aurora-purple focus:shadow-[0_0_0_3px_rgba(99,102,241,0.2)]',
          icon ? 'pl-11' : '',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
      />
    </div>
  )
}