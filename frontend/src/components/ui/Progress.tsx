import { HTMLAttributes } from 'react'
import { clsx } from 'clsx'

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number
  max?: number
  variant?: 'bar' | 'ring' | 'steps'
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
  color?: 'primary' | 'success' | 'warning' | 'error'
  steps?: number
}

export default function Progress({
  value,
  max = 100,
  variant = 'bar',
  size = 'md',
  showValue = false,
  color = 'primary',
  steps,
  className,
  ...props
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  const colorClasses = {
    primary: 'bg-primary-500',
    success: 'bg-success-500',
    warning: 'bg-warning-500',
    error: 'bg-error-500',
  }

  const sizeClasses = {
    bar: {
      sm: 'h-1.5',
      md: 'h-2.5',
      lg: 'h-3.5',
    },
    ring: {
      sm: 'w-12 h-12',
      md: 'w-16 h-16',
      lg: 'w-24 h-24',
    },
  }

  if (variant === 'ring') {
    const strokeWidth = size === 'sm' ? 4 : size === 'md' ? 6 : 8
    const radius = size === 'sm' ? 20 : size === 'md' ? 28 : 44
    const circumference = 2 * Math.PI * radius
    const strokeDashoffset = circumference - (percentage / 100) * circumference

    return (
      <div className={clsx('relative inline-flex items-center justify-center', className)} {...props}>
        <svg
          className={clsx(sizeClasses.ring[size], 'transform -rotate-90')}
          viewBox="0 0 100 100"
        >
          <circle
            cx="50"
            cy="50"
            r={radius}
            className="stroke-gray-200 dark:stroke-gray-700"
            strokeWidth={strokeWidth}
            fill="none"
          />
          <circle
            cx="50"
            cy="50"
            r={radius}
            className={clsx(colorClasses[color], 'transition-all duration-500 ease-out')}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
          />
        </svg>
        {showValue && (
          <span className="absolute text-sm font-semibold text-gray-700 dark:text-gray-300">
            {Math.round(percentage)}%
          </span>
        )}
      </div>
    )
  }

  if (variant === 'steps' && steps) {
    const currentStep = Math.ceil((value / max) * steps)
    return (
      <div className={clsx('flex gap-2', className)} {...props}>
        {Array.from({ length: steps }).map((_, index) => (
          <div
            key={index}
            className={clsx(
              'flex-1 h-2 rounded-full transition-all duration-300',
              index < currentStep
                ? colorClasses[color]
                : 'bg-gray-200 dark:bg-gray-700'
            )}
          />
        ))}
      </div>
    )
  }

  return (
    <div className={clsx('w-full', className)} {...props}>
      <div className={clsx('w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden', sizeClasses.bar[size])}>
        <div
          className={clsx(
            colorClasses[color],
            'h-full transition-all duration-500 ease-out rounded-full'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showValue && (
        <div className="mt-1 text-xs text-gray-600 dark:text-gray-400 text-right">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  )
}
