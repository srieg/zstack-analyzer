import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

interface QuickAction {
  id: string
  label: string
  icon: React.ReactNode
  onClick: () => void
  color: string
  show?: boolean
}

interface QuickActionsProps {
  onRunAnalysis?: () => void
  onValidate?: () => void
  onShowShortcuts?: () => void
}

export default function QuickActions({
  onRunAnalysis,
  onValidate,
  onShowShortcuts,
}: QuickActionsProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const isViewer = location.pathname.includes('/images/')

  const actions: QuickAction[] = [
    {
      id: 'upload',
      label: 'New Upload',
      color: 'bg-blue-500 hover:bg-blue-600',
      show: true,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
      ),
      onClick: () => {
        navigate('/upload')
        setIsExpanded(false)
      },
    },
    {
      id: 'analysis',
      label: 'Run Analysis',
      color: 'bg-green-500 hover:bg-green-600',
      show: isViewer && !!onRunAnalysis,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
      onClick: () => {
        onRunAnalysis?.()
        setIsExpanded(false)
      },
    },
    {
      id: 'validate',
      label: 'Validate',
      color: 'bg-purple-500 hover:bg-purple-600',
      show: isViewer && !!onValidate,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
      onClick: () => {
        onValidate?.()
        setIsExpanded(false)
      },
    },
    {
      id: 'shortcuts',
      label: 'Shortcuts',
      color: 'bg-gray-600 hover:bg-gray-700',
      show: true,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
      onClick: () => {
        onShowShortcuts?.()
        setIsExpanded(false)
      },
    },
  ]

  const visibleActions = actions.filter((a) => a.show !== false)

  return (
    <div className="fixed bottom-6 right-6 z-40 md:hidden">
      {/* Action buttons (expanded state) */}
      {isExpanded && (
        <div className="mb-4 flex flex-col gap-3 animate-slide-up">
          {visibleActions.map((action, index) => (
            <button
              key={action.id}
              onClick={action.onClick}
              className={`${action.color} text-white p-4 rounded-full shadow-lg transition-all transform hover:scale-110 flex items-center gap-3`}
              style={{
                animationDelay: `${index * 50}ms`,
              }}
            >
              {action.icon}
              <span className="text-sm font-medium pr-2">{action.label}</span>
            </button>
          ))}
        </div>
      )}

      {/* Main FAB button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`${
          isExpanded
            ? 'bg-red-500 hover:bg-red-600 rotate-45'
            : 'bg-primary-600 hover:bg-primary-700'
        } text-white p-5 rounded-full shadow-2xl transition-all transform hover:scale-110 flex items-center justify-center`}
      >
        {isExpanded ? (
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
        )}
      </button>

      {/* Backdrop */}
      {isExpanded && (
        <div
          className="fixed inset-0 bg-black/20 -z-10"
          onClick={() => setIsExpanded(false)}
        />
      )}
    </div>
  )
}
