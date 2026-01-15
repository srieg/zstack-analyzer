import { useEffect, useState } from 'react'

interface Tech {
  name: string
  logo: string
  color: string
}

const technologies: Tech[] = [
  { name: 'Python', logo: '🐍', color: 'text-yellow-400' },
  { name: 'tinygrad', logo: '⚡', color: 'text-purple-400' },
  { name: 'React', logo: '⚛️', color: 'text-blue-400' },
  { name: 'TypeScript', logo: '📘', color: 'text-blue-500' },
  { name: 'FastAPI', logo: '🚀', color: 'text-green-400' },
  { name: 'Three.js', logo: '🎲', color: 'text-white' },
  { name: 'Tailwind', logo: '💨', color: 'text-cyan-400' },
  { name: 'WebGL', logo: '🎨', color: 'text-pink-400' },
]

export default function TechStack() {
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % technologies.length)
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative overflow-hidden py-12">
      {/* Marquee container */}
      <div className="flex space-x-8 animate-marquee">
        {[...technologies, ...technologies].map((tech, index) => (
          <div
            key={index}
            className={`
              flex flex-col items-center justify-center min-w-[120px] p-6
              bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50
              transition-all duration-500
              ${
                index % technologies.length === activeIndex
                  ? 'scale-110 border-blue-500/50 shadow-lg shadow-blue-500/20'
                  : 'scale-100'
              }
            `}
          >
            <div className="text-5xl mb-3">{tech.logo}</div>
            <div className={`text-sm font-semibold ${tech.color}`}>
              {tech.name}
            </div>
          </div>
        ))}
      </div>

      {/* Fade edges */}
      <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-slate-900 to-transparent pointer-events-none" />
      <div className="absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-slate-900 to-transparent pointer-events-none" />

      <style>{`
        @keyframes marquee {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }

        .animate-marquee {
          animation: marquee 20s linear infinite;
        }

        .animate-marquee:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  )
}
