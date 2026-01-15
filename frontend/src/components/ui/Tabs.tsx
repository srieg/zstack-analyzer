import { ReactNode, useState } from 'react'
import { clsx } from 'clsx'

export interface Tab {
  id: string
  label: string
  icon?: ReactNode
  content: ReactNode
  disabled?: boolean
}

export interface TabsProps {
  tabs: Tab[]
  defaultTab?: string
  onChange?: (tabId: string) => void
  variant?: 'line' | 'pills' | 'enclosed'
}

export default function Tabs({
  tabs,
  defaultTab,
  onChange,
  variant = 'line',
}: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id)

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId)
    onChange?.(tabId)
  }

  const activeTabContent = tabs.find((tab) => tab.id === activeTab)?.content

  return (
    <div className="w-full">
      {/* Tab List */}
      <div
        className={clsx(
          'flex gap-1',
          variant === 'line' && 'border-b border-gray-200 dark:border-gray-700',
          variant === 'pills' && 'bg-gray-100 dark:bg-gray-800 p-1 rounded-lg',
          variant === 'enclosed' && 'border-b border-gray-200 dark:border-gray-700'
        )}
        role="tablist"
      >
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.id}`}
              disabled={tab.disabled}
              onClick={() => !tab.disabled && handleTabChange(tab.id)}
              className={clsx(
                'relative px-4 py-2.5 text-sm font-medium transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-primary-500/20 rounded-lg',
                'disabled:opacity-50 disabled:cursor-not-allowed',

                // Line variant
                variant === 'line' && [
                  'border-b-2',
                  isActive
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200',
                ],

                // Pills variant
                variant === 'pills' && [
                  isActive
                    ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200',
                ],

                // Enclosed variant
                variant === 'enclosed' && [
                  'border border-transparent -mb-px',
                  isActive
                    ? 'border-gray-200 dark:border-gray-700 border-b-white dark:border-b-gray-800 bg-white dark:bg-gray-800 rounded-t-lg'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200',
                ]
              )}
            >
              <span className="flex items-center gap-2">
                {tab.icon && <span className="flex-shrink-0">{tab.icon}</span>}
                {tab.label}
              </span>

              {/* Animated indicator for line variant */}
              {variant === 'line' && isActive && (
                <span
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500 animate-scale-in"
                  style={{ transformOrigin: 'left' }}
                />
              )}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div
        role="tabpanel"
        id={`tabpanel-${activeTab}`}
        className="mt-4 animate-fade-in"
      >
        {activeTabContent}
      </div>
    </div>
  )
}
