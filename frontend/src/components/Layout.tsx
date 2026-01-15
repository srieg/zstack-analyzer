import { ReactNode, useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  HomeIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  ChartBarIcon,
  Bars3Icon,
  XMarkIcon,
  MoonIcon,
  SunIcon,
  CommandLineIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Upload', href: '/upload', icon: CloudArrowUpIcon },
  { name: 'Validation', href: '/validation', icon: CheckCircleIcon },
  { name: 'Results', href: '/results', icon: ChartBarIcon },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)

  // Initialize dark mode from localStorage or system preference
  useEffect(() => {
    const isDark = localStorage.getItem('darkMode') === 'true' ||
      (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)
    setDarkMode(isDark)
    if (isDark) {
      document.documentElement.classList.add('dark')
    }
  }, [])

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newMode = !darkMode
    setDarkMode(newMode)
    localStorage.setItem('darkMode', String(newMode))
    if (newMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // Command palette keyboard shortcut (Cmd+K / Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
      }
      // ESC to close
      if (e.key === 'Escape') {
        setCommandPaletteOpen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Generate breadcrumbs from current path
  const pathSegments = location.pathname.split('/').filter(Boolean)
  const breadcrumbs = [
    { name: 'Home', path: '/' },
    ...pathSegments.map((segment, index) => ({
      name: segment.charAt(0).toUpperCase() + segment.slice(1),
      path: '/' + pathSegments.slice(0, index + 1).join('/'),
    })),
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-200">
      {/* Command Palette Overlay */}
      {commandPaletteOpen && (
        <div
          className="fixed inset-0 z-50 bg-gray-900/50 dark:bg-gray-950/80 backdrop-blur-sm animate-fade-in"
          onClick={() => setCommandPaletteOpen(false)}
        >
          <div className="flex items-start justify-center pt-20 px-4">
            <div
              className="w-full max-w-2xl glass-strong rounded-2xl shadow-2xl animate-scale-in"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center gap-3 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
                <CommandLineIcon className="h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Type a command or search..."
                  className="flex-1 bg-transparent border-none outline-none text-gray-900 dark:text-gray-100 placeholder-gray-500"
                  autoFocus
                />
                <kbd className="px-2 py-1 text-xs font-semibold text-gray-500 bg-gray-100 dark:bg-gray-800 rounded">
                  ESC
                </kbd>
              </div>
              <div className="p-2 max-h-96 overflow-y-auto">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setCommandPaletteOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  >
                    <item.icon className="h-5 w-5 text-gray-500" />
                    <span className="text-gray-900 dark:text-gray-100">{item.name}</span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-40 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800',
          'transition-all duration-300 ease-in-out',
          sidebarCollapsed ? 'w-20' : 'w-64',
          'shadow-lg'
        )}
      >
        {/* Logo / Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200 dark:border-gray-800">
          {!sidebarCollapsed && (
            <h1 className="text-xl font-bold bg-gradient-scientific bg-clip-text text-transparent animate-fade-in">
              Z-Stack Analyzer
            </h1>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle sidebar"
          >
            {sidebarCollapsed ? (
              <Bars3Icon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            ) : (
              <XMarkIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          <ul className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={clsx(
                      'group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg',
                      'transition-all duration-200',
                      isActive
                        ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400'
                        : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-300',
                      sidebarCollapsed && 'justify-center'
                    )}
                    title={sidebarCollapsed ? item.name : undefined}
                  >
                    <item.icon
                      className={clsx(
                        'h-5 w-5 flex-shrink-0 transition-colors',
                        isActive ? 'text-primary-500' : 'text-gray-500 dark:text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-400',
                        !sidebarCollapsed && 'mr-3'
                      )}
                    />
                    {!sidebarCollapsed && (
                      <span className="truncate">{item.name}</span>
                    )}
                    {isActive && !sidebarCollapsed && (
                      <span className="ml-auto w-1.5 h-8 bg-primary-500 rounded-full animate-scale-in" />
                    )}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Bottom Controls */}
        <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-gray-200 dark:border-gray-800 space-y-2">
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className={clsx(
              'w-full flex items-center gap-3 px-3 py-2 rounded-lg',
              'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
              'transition-colors',
              sidebarCollapsed && 'justify-center'
            )}
            title="Command Palette (⌘K)"
          >
            <CommandLineIcon className="h-5 w-5 flex-shrink-0" />
            {!sidebarCollapsed && (
              <span className="text-sm flex-1 text-left">Command Palette</span>
            )}
            {!sidebarCollapsed && (
              <kbd className="px-1.5 py-0.5 text-xs font-semibold bg-gray-100 dark:bg-gray-800 rounded">
                ⌘K
              </kbd>
            )}
          </button>
          <button
            onClick={toggleDarkMode}
            className={clsx(
              'w-full flex items-center gap-3 px-3 py-2 rounded-lg',
              'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
              'transition-colors',
              sidebarCollapsed && 'justify-center'
            )}
            title={darkMode ? 'Light Mode' : 'Dark Mode'}
          >
            {darkMode ? (
              <SunIcon className="h-5 w-5 flex-shrink-0" />
            ) : (
              <MoonIcon className="h-5 w-5 flex-shrink-0" />
            )}
            {!sidebarCollapsed && (
              <span className="text-sm">{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
            )}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className={clsx('transition-all duration-300', sidebarCollapsed ? 'pl-20' : 'pl-64')}>
        {/* Header with Breadcrumbs and Status Bar */}
        <header className="sticky top-0 z-30 glass-strong border-b border-gray-200 dark:border-gray-800">
          <div className="mx-auto max-w-7xl px-6 lg:px-8 py-3">
            {/* Breadcrumbs */}
            <nav className="flex items-center space-x-2 text-sm">
              {breadcrumbs.map((crumb, index) => (
                <div key={crumb.path} className="flex items-center">
                  {index > 0 && (
                    <span className="mx-2 text-gray-400 dark:text-gray-600">/</span>
                  )}
                  <Link
                    to={crumb.path}
                    className={clsx(
                      'transition-colors',
                      index === breadcrumbs.length - 1
                        ? 'text-gray-900 dark:text-gray-100 font-medium'
                        : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                    )}
                  >
                    {crumb.name}
                  </Link>
                </div>
              ))}
            </nav>
          </div>
        </header>

        {/* Status Bar */}
        <div className="bg-gray-100 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
          <div className="mx-auto max-w-7xl px-6 lg:px-8 py-2">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <CpuChipIcon className="h-4 w-4 text-success-500 animate-pulse" />
                  <span className="text-gray-600 dark:text-gray-400">GPU: Ready</span>
                </div>
                <div className="h-3 w-px bg-gray-300 dark:bg-gray-700" />
                <span className="text-gray-600 dark:text-gray-400">Processing: 0 active</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-success-500 animate-pulse-glow" />
                <span className="text-gray-600 dark:text-gray-400">System Ready</span>
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="py-8 animate-fade-in">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
