import { ReactNode, useState } from 'react'

interface FeatureCardProps {
  icon: ReactNode
  title: string
  description: string
  delay?: number
}

export default function FeatureCard({
  icon,
  title,
  description,
  delay = 0,
}: FeatureCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className="group relative"
      style={{
        animation: `fadeInUp 0.6s ease-out ${delay}s both`,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div
        className={`
        relative p-6 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50
        transition-all duration-300
        ${isHovered ? 'transform -translate-y-2 border-blue-500/50 shadow-lg shadow-blue-500/20' : ''}
      `}
      >
        {/* Gradient overlay on hover */}
        <div
          className={`
          absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-xl
          transition-opacity duration-300
          ${isHovered ? 'opacity-100' : 'opacity-0'}
        `}
        />

        {/* Content */}
        <div className="relative z-10">
          <div
            className={`
            inline-flex p-3 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600
            transition-transform duration-300
            ${isHovered ? 'transform rotate-6 scale-110' : ''}
          `}
          >
            {icon}
          </div>

          <h3 className="mt-4 text-xl font-semibold text-white">{title}</h3>

          <p className="mt-2 text-slate-400 leading-relaxed">{description}</p>

          {/* Animated arrow */}
          <div
            className={`
            mt-4 flex items-center text-blue-400 text-sm font-medium
            transition-transform duration-300
            ${isHovered ? 'transform translate-x-2' : ''}
          `}
          >
            Learn more
            <svg
              className="ml-2 w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}
