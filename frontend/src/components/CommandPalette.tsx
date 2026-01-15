import { useState, useEffect, useRef, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { shortcuts, categoryLabels, formatShortcut, type ShortcutCategory } from '@/config/shortcuts'

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
  onExecuteAction: (action: string) => void
}

interface CommandItem {
  id: string
  title: string
  description: string
  category: ShortcutCategory
  action: string
  shortcut: string
}

export default function CommandPalette({ isOpen, onClose, onExecuteAction }: CommandPaletteProps) {
  const [search, setSearch] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [recentActions, setRecentActions] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  // Build command items from shortcuts
  const commands: CommandItem[] = useMemo(
    () =>
      shortcuts.map((s) => ({
        id: s.action,
        title: s.description,
        description: `${categoryLabels[s.category]} • ${s.context || 'Global'}`,
        category: s.category,
        action: s.action,
        shortcut: formatShortcut(s),
      })),
    []
  )

  // Fuzzy search implementation
  const filteredCommands = useMemo(() => {
    if (!search) return commands

    const searchLower = search.toLowerCase()
    return commands
      .map((cmd) => {
        const titleLower = cmd.title.toLowerCase()
        const descLower = cmd.description.toLowerCase()

        // Calculate match score
        let score = 0
        if (titleLower.includes(searchLower)) score += 10
        if (descLower.includes(searchLower)) score += 5
        if (titleLower.startsWith(searchLower)) score += 5

        // Check for fuzzy match
        let fuzzyScore = 0
        let searchIndex = 0
        for (let i = 0; i < titleLower.length && searchIndex < searchLower.length; i++) {
          if (titleLower[i] === searchLower[searchIndex]) {
            fuzzyScore++
            searchIndex++
          }
        }
        if (searchIndex === searchLower.length) {
          score += fuzzyScore
        }

        return { ...cmd, score }
      })
      .filter((cmd) => cmd.score > 0)
      .sort((a, b) => b.score - a.score)
  }, [commands, search])

  // Group commands by category
  const groupedCommands = useMemo(() => {
    const groups: Record<ShortcutCategory, CommandItem[]> = {
      navigation: [],
      actions: [],
      viewer: [],
      settings: [],
      help: [],
    }

    filteredCommands.forEach((cmd) => {
      groups[cmd.category].push(cmd)
    })

    return groups
  }, [filteredCommands])

  // Recent actions
  const recentCommands = useMemo(() => {
    return commands.filter((cmd) => recentActions.includes(cmd.action)).slice(0, 5)
  }, [commands, recentActions])

  // Reset selection when search changes
  useEffect(() => {
    setSelectedIndex(0)
  }, [search])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((i) => Math.min(i + 1, filteredCommands.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((i) => Math.max(i - 1, 0))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (filteredCommands[selectedIndex]) {
          executeCommand(filteredCommands[selectedIndex])
        }
      } else if (e.key === 'Escape') {
        e.preventDefault()
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredCommands, selectedIndex])

  // Execute command
  const executeCommand = (command: CommandItem) => {
    // Add to recent actions
    setRecentActions((prev) => {
      const filtered = prev.filter((a) => a !== command.action)
      return [command.action, ...filtered].slice(0, 10)
    })

    // Handle navigation commands
    if (command.action.startsWith('navigate_')) {
      const path = command.action.replace('navigate_', '')
      switch (path) {
        case 'dashboard':
          navigate('/')
          break
        case 'upload':
          navigate('/upload')
          break
        case 'validation':
          navigate('/validation')
          break
        case 'results':
          navigate('/results')
          break
        case 'images':
          // Navigate to first image or stay on dashboard
          navigate('/')
          break
      }
    } else {
      // Execute custom action
      onExecuteAction(command.action)
    }

    // Close palette
    setSearch('')
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
      {/* Backdrop with blur */}
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Command palette */}
      <div className="relative w-full max-w-2xl mx-4 bg-white rounded-lg shadow-2xl overflow-hidden animate-slide-down">
        {/* Search input */}
        <div className="border-b border-gray-200 p-4">
          <div className="flex items-center space-x-3">
            <svg
              className="w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              ref={inputRef}
              type="text"
              placeholder="Search commands..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 text-lg outline-none"
            />
            <kbd className="hidden sm:inline-flex items-center px-2 py-1 text-xs font-semibold text-gray-600 bg-gray-100 border border-gray-200 rounded">
              ESC
            </kbd>
          </div>
        </div>

        {/* Command list */}
        <div className="max-h-[60vh] overflow-y-auto">
          {/* Recent actions */}
          {!search && recentCommands.length > 0 && (
            <div className="py-2">
              <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">
                Recent
              </div>
              {recentCommands.map((cmd) => (
                <CommandListItem
                  key={cmd.id}
                  command={cmd}
                  isSelected={false}
                  onClick={() => executeCommand(cmd)}
                />
              ))}
            </div>
          )}

          {/* Grouped commands */}
          {Object.entries(groupedCommands).map(([category, cmds]) => {
            if (cmds.length === 0) return null

            return (
              <div key={category} className="py-2">
                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">
                  {categoryLabels[category as ShortcutCategory]}
                </div>
                {cmds.map((cmd) => {
                  const globalIndex = filteredCommands.findIndex((c) => c.id === cmd.id)
                  return (
                    <CommandListItem
                      key={cmd.id}
                      command={cmd}
                      isSelected={globalIndex === selectedIndex}
                      onClick={() => executeCommand(cmd)}
                    />
                  )
                })}
              </div>
            )
          })}

          {/* No results */}
          {filteredCommands.length === 0 && search && (
            <div className="py-12 text-center text-gray-500">
              <p>No commands found for "{search}"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

interface CommandListItemProps {
  command: CommandItem
  isSelected: boolean
  onClick: () => void
}

function CommandListItem({ command, isSelected, onClick }: CommandListItemProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isSelected && ref.current) {
      ref.current.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [isSelected])

  return (
    <div
      ref={ref}
      onClick={onClick}
      className={`px-4 py-3 cursor-pointer transition-colors ${
        isSelected ? 'bg-primary-50 border-l-2 border-primary-500' : 'hover:bg-gray-50'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-gray-900">{command.title}</div>
          <div className="text-xs text-gray-500 mt-1">{command.description}</div>
        </div>
        <kbd className="ml-4 inline-flex items-center px-2 py-1 text-xs font-semibold text-gray-600 bg-gray-100 border border-gray-200 rounded whitespace-nowrap">
          {command.shortcut}
        </kbd>
      </div>
    </div>
  )
}
