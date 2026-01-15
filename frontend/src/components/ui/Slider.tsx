import { InputHTMLAttributes, forwardRef, useState, useEffect } from 'react'
import { clsx } from 'clsx'

export interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> {
  label?: string
  min?: number
  max?: number
  step?: number
  value?: number
  onChange?: (value: number) => void
  showValue?: boolean
  unit?: string
  color?: 'primary' | 'success' | 'warning' | 'error'
}

const Slider = forwardRef<HTMLInputElement, SliderProps>(
  (
    {
      label,
      min = 0,
      max = 100,
      step = 1,
      value: controlledValue,
      onChange,
      showValue = true,
      unit = '',
      color = 'primary',
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const [value, setValue] = useState(controlledValue || min)

    useEffect(() => {
      if (controlledValue !== undefined) {
        setValue(controlledValue)
      }
    }, [controlledValue])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = Number(e.target.value)
      setValue(newValue)
      onChange?.(newValue)
    }

    const percentage = ((value - min) / (max - min)) * 100

    return (
      <div className={clsx('w-full', className)}>
        {(label || showValue) && (
          <div className="flex items-center justify-between mb-2">
            {label && (
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {label}
              </label>
            )}
            {showValue && (
              <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {value}{unit}
              </span>
            )}
          </div>
        )}
        <div className="relative">
          <input
            ref={ref}
            type="range"
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={handleChange}
            disabled={disabled}
            className={clsx(
              'w-full h-2 rounded-lg appearance-none cursor-pointer',
              'bg-gray-200 dark:bg-gray-700',
              'focus:outline-none focus:ring-2 focus:ring-offset-2',
              color === 'primary' && 'focus:ring-primary-500',
              color === 'success' && 'focus:ring-success-500',
              color === 'warning' && 'focus:ring-warning-500',
              color === 'error' && 'focus:ring-error-500',
              disabled && 'opacity-50 cursor-not-allowed',
              '[&::-webkit-slider-thumb]:appearance-none',
              '[&::-webkit-slider-thumb]:w-5',
              '[&::-webkit-slider-thumb]:h-5',
              '[&::-webkit-slider-thumb]:rounded-full',
              '[&::-webkit-slider-thumb]:bg-white',
              '[&::-webkit-slider-thumb]:shadow-md',
              '[&::-webkit-slider-thumb]:border-2',
              color === 'primary' && '[&::-webkit-slider-thumb]:border-primary-500',
              color === 'success' && '[&::-webkit-slider-thumb]:border-success-500',
              color === 'warning' && '[&::-webkit-slider-thumb]:border-warning-500',
              color === 'error' && '[&::-webkit-slider-thumb]:border-error-500',
              '[&::-webkit-slider-thumb]:transition-transform',
              '[&::-webkit-slider-thumb]:hover:scale-110',
              '[&::-moz-range-thumb]:w-5',
              '[&::-moz-range-thumb]:h-5',
              '[&::-moz-range-thumb]:rounded-full',
              '[&::-moz-range-thumb]:bg-white',
              '[&::-moz-range-thumb]:border-2',
              color === 'primary' && '[&::-moz-range-thumb]:border-primary-500',
              color === 'success' && '[&::-moz-range-thumb]:border-success-500',
              color === 'warning' && '[&::-moz-range-thumb]:border-warning-500',
              color === 'error' && '[&::-moz-range-thumb]:border-error-500',
              '[&::-moz-range-thumb]:transition-transform',
              '[&::-moz-range-thumb]:hover:scale-110'
            )}
            style={{
              background: `linear-gradient(to right, ${
                color === 'primary' ? '#14b8a6' :
                color === 'success' ? '#22c55e' :
                color === 'warning' ? '#f59e0b' :
                '#ef4444'
              } 0%, ${
                color === 'primary' ? '#14b8a6' :
                color === 'success' ? '#22c55e' :
                color === 'warning' ? '#f59e0b' :
                '#ef4444'
              } ${percentage}%, #e4e4e7 ${percentage}%, #e4e4e7 100%)`,
            }}
            {...props}
          />
        </div>
        <div className="flex justify-between mt-1 text-xs text-gray-500 dark:text-gray-400">
          <span>{min}{unit}</span>
          <span>{max}{unit}</span>
        </div>
      </div>
    )
  }
)

Slider.displayName = 'Slider'

export default Slider
