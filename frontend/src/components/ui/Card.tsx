import { HTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'hover' | 'glass'
  loading?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant = 'default',
      loading = false,
      padding = 'md',
      children,
      ...props
    },
    ref
  ) => {
    const variantClasses = {
      default: 'card',
      hover: 'card-hover',
      glass: 'card-glass',
    }

    const paddingClasses = {
      none: 'p-0',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    }

    if (loading) {
      return (
        <div
          ref={ref}
          className={clsx(variantClasses[variant], paddingClasses[padding], className)}
          {...props}
        >
          <div className="space-y-3">
            <div className="skeleton-text h-6 w-3/4" />
            <div className="skeleton-text h-4 w-full" />
            <div className="skeleton-text h-4 w-5/6" />
          </div>
        </div>
      )
    }

    return (
      <div
        ref={ref}
        className={clsx(
          variantClasses[variant],
          paddingClasses[padding],
          'animate-fade-in',
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

export default Card
