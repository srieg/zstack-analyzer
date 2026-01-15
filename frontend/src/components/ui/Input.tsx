import { InputHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'
import { ExclamationCircleIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  success?: string
  helperText?: string
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      label,
      error,
      success,
      helperText,
      icon,
      iconPosition = 'left',
      disabled,
      ...props
    },
    ref
  ) => {
    const hasError = !!error
    const hasSuccess = !!success
    const hasIcon = !!icon

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            {label}
          </label>
        )}
        <div className="relative">
          {hasIcon && iconPosition === 'left' && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400">{icon}</span>
            </div>
          )}
          <input
            ref={ref}
            disabled={disabled}
            className={clsx(
              'input',
              hasIcon && iconPosition === 'left' && 'pl-10',
              hasIcon && iconPosition === 'right' && 'pr-10',
              hasError && 'input-error',
              hasSuccess && 'border-success-500 focus:border-success-500 focus:ring-success-500/20',
              disabled && 'opacity-50 cursor-not-allowed bg-gray-50 dark:bg-gray-900',
              className
            )}
            {...props}
          />
          {hasIcon && iconPosition === 'right' && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-gray-400">{icon}</span>
            </div>
          )}
          {hasError && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <ExclamationCircleIcon className="h-5 w-5 text-error-500" />
            </div>
          )}
          {hasSuccess && !hasError && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <CheckCircleIcon className="h-5 w-5 text-success-500" />
            </div>
          )}
        </div>
        {(error || success || helperText) && (
          <p
            className={clsx(
              'mt-1.5 text-sm',
              error && 'text-error-600 dark:text-error-400',
              success && 'text-success-600 dark:text-success-400',
              !error && !success && 'text-gray-500 dark:text-gray-400'
            )}
          >
            {error || success || helperText}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
