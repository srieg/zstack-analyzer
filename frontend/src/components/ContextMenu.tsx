import { useEffect, useRef, useState } from 'react'

export type ContextMenuItem =
  | {
      id: string
      separator: true
      label?: string
      icon?: never
      shortcut?: never
      disabled?: never
      danger?: never
      onClick?: never
    }
  | {
      id: string
      label: string
      separator?: false
      icon?: React.ReactNode
      shortcut?: string
      disabled?: boolean
      danger?: boolean
      onClick?: () => void
    }

interface ContextMenuProps {
  items: ContextMenuItem[]
  isOpen: boolean
  position: { x: number; y: number }
  onClose: () => void
}

export default function ContextMenu({ items, isOpen, position, onClose }: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)
  const [adjustedPosition, setAdjustedPosition] = useState(position)

  // Adjust position to keep menu in viewport
  useEffect(() => {
    if (!isOpen || !menuRef.current) return

    const menu = menuRef.current
    const menuRect = menu.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    let { x, y } = position

    // Adjust horizontal position
    if (x + menuRect.width > viewportWidth) {
      x = viewportWidth - menuRect.width - 10
    }

    // Adjust vertical position
    if (y + menuRect.height > viewportHeight) {
      y = viewportHeight - menuRect.height - 10
    }

    setAdjustedPosition({ x, y })
  }, [isOpen, position])

  // Close on click outside or escape
  useEffect(() => {
    if (!isOpen) return

    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose()
      }
    }

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <>
      {/* Invisible backdrop to catch clicks */}
      <div className="fixed inset-0 z-40" onClick={onClose} />

      {/* Context menu */}
      <div
        ref={menuRef}
        className="fixed z-50 w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-1 animate-scale-in"
        style={{
          left: `${adjustedPosition.x}px`,
          top: `${adjustedPosition.y}px`,
        }}
      >
        {items.map((item, index) => {
          if (item.separator) {
            return <div key={`separator-${index}`} className="my-1 border-t border-gray-200" />
          }

          return (
            <button
              key={item.id}
              onClick={() => {
                if (!item.disabled && item.onClick) {
                  item.onClick()
                  onClose()
                }
              }}
              disabled={item.disabled}
              className={`w-full px-4 py-2 text-left text-sm flex items-center justify-between transition-colors ${
                item.disabled
                  ? 'text-gray-400 cursor-not-allowed'
                  : item.danger
                  ? 'text-red-700 hover:bg-red-50'
                  : 'text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center gap-3">
                {item.icon && <span className="w-4 h-4 flex-shrink-0">{item.icon}</span>}
                <span>{item.label}</span>
              </div>

              {item.shortcut && (
                <kbd className="ml-4 text-xs text-gray-500 font-semibold">{item.shortcut}</kbd>
              )}
            </button>
          )
        })}
      </div>
    </>
  )
}

// Hook for managing context menu
export function useContextMenu() {
  const [isOpen, setIsOpen] = useState(false)
  const [position, setPosition] = useState({ x: 0, y: 0 })

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault()
    setPosition({ x: e.clientX, y: e.clientY })
    setIsOpen(true)
  }

  const closeMenu = () => setIsOpen(false)

  return {
    isOpen,
    position,
    handleContextMenu,
    closeMenu,
  }
}
