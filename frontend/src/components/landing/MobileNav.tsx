import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'

export default function MobileNav() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-6 right-6 z-50 p-3 bg-slate-800/90 backdrop-blur-sm rounded-lg border border-slate-700/50 hover:border-blue-500/50 transition-all duration-300 md:hidden"
      >
        {isOpen ? (
          <XMarkIcon className="w-6 h-6 text-white" />
        ) : (
          <Bars3Icon className="w-6 h-6 text-white" />
        )}
      </button>

      {/* Mobile menu overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Mobile menu panel */}
      <div
        className={`
          fixed top-0 right-0 bottom-0 z-40 w-72 bg-slate-900 border-l border-slate-800
          transform transition-transform duration-300 ease-in-out md:hidden
          ${isOpen ? 'translate-x-0' : 'translate-x-full'}
        `}
      >
        <nav className="flex flex-col h-full p-8 pt-24">
          <div className="flex flex-col space-y-6">
            <a
              href="#features"
              className="text-lg text-slate-300 hover:text-white transition-colors"
              onClick={() => setIsOpen(false)}
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="text-lg text-slate-300 hover:text-white transition-colors"
              onClick={() => setIsOpen(false)}
            >
              How It Works
            </a>
            <a
              href="#performance"
              className="text-lg text-slate-300 hover:text-white transition-colors"
              onClick={() => setIsOpen(false)}
            >
              Performance
            </a>
            <a
              href="https://docs.zstack-analyzer.dev"
              target="_blank"
              rel="noopener noreferrer"
              className="text-lg text-slate-300 hover:text-white transition-colors"
            >
              Documentation
            </a>
          </div>

          <div className="mt-auto space-y-4">
            <Link
              to="/app"
              className="block w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold text-center hover:shadow-lg hover:shadow-purple-500/50 transition-all duration-300"
              onClick={() => setIsOpen(false)}
            >
              Try Demo
            </Link>
            <a
              href="https://github.com/yourusername/zstack-analyzer"
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full px-6 py-3 bg-slate-800 border border-slate-700 rounded-lg font-semibold text-center hover:border-blue-500/50 transition-all duration-300"
              onClick={() => setIsOpen(false)}
            >
              GitHub
            </a>
          </div>
        </nav>
      </div>
    </>
  )
}
