import { useEffect, useRef, useState } from 'react'

interface StatsCounterProps {
  end: number
  duration?: number
  suffix?: string
  prefix?: string
  decimals?: number
  label: string
}

export default function StatsCounter({
  end,
  duration = 2000,
  suffix = '',
  prefix = '',
  decimals = 0,
  label,
}: StatsCounterProps) {
  const [count, setCount] = useState(0)
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1 }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [])

  useEffect(() => {
    if (!isVisible) return

    const startTime = Date.now()
    const startValue = 0

    const animate = () => {
      const now = Date.now()
      const progress = Math.min((now - startTime) / duration, 1)

      // Easing function for smooth animation
      const easeOutQuart = 1 - Math.pow(1 - progress, 4)
      const currentCount = startValue + (end - startValue) * easeOutQuart

      setCount(currentCount)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [isVisible, end, duration])

  const displayValue = decimals > 0
    ? count.toFixed(decimals)
    : Math.floor(count).toString()

  return (
    <div
      ref={ref}
      className="flex flex-col items-center justify-center p-6 bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700/50 hover:border-blue-500/50 transition-all duration-300 hover:scale-105"
    >
      <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
        {prefix}
        {displayValue}
        {suffix}
      </div>
      <div className="text-slate-400 text-sm mt-2">{label}</div>
    </div>
  )
}
