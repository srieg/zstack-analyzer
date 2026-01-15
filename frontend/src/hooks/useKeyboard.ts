import { useEffect, useRef, useCallback } from 'react'
import { useLocation } from 'react-router-dom'
import { shortcuts, type KeyboardShortcut } from '@/config/shortcuts'

type ShortcutHandler = (action: string) => void
type ContextType = 'global' | 'viewer' | 'dashboard' | 'upload' | 'validation' | 'results'

interface UseKeyboardOptions {
  enabled?: boolean
  context?: ContextType
  onShortcut: ShortcutHandler
}

/**
 * Global keyboard shortcut manager with context awareness
 * Prevents conflicts with browser shortcuts and supports key sequences
 */
export function useKeyboard({ enabled = true, context = 'global', onShortcut }: UseKeyboardOptions) {
  const location = useLocation()
  const sequenceBuffer = useRef<string[]>([])
  const sequenceTimeout = useRef<NodeJS.Timeout>()

  // Determine current context from route
  const getCurrentContext = useCallback((): ContextType => {
    const path = location.pathname
    if (path.includes('/images/')) return 'viewer'
    if (path.includes('/upload')) return 'upload'
    if (path.includes('/validation')) return 'validation'
    if (path.includes('/results')) return 'results'
    if (path === '/') return 'dashboard'
    return 'global'
  }, [location.pathname])

  // Check if element should be ignored (input fields, textareas, etc)
  const shouldIgnoreTarget = useCallback((target: EventTarget | null): boolean => {
    if (!target) return false

    const element = target as HTMLElement
    const tagName = element.tagName.toLowerCase()
    const isContentEditable = element.isContentEditable

    return (
      tagName === 'input' ||
      tagName === 'textarea' ||
      tagName === 'select' ||
      isContentEditable ||
      element.getAttribute('role') === 'textbox'
    )
  }, [])

  // Match shortcut based on key event
  const matchShortcut = useCallback(
    (e: KeyboardEvent, currentContext: ContextType): KeyboardShortcut | null => {
      // Check for modifier key shortcuts
      for (const shortcut of shortcuts) {
        if (shortcut.requiresMod || shortcut.requiresShift || shortcut.requiresAlt) {
          const modKey = e.metaKey || e.ctrlKey
          const shiftKey = e.shiftKey
          const altKey = e.altKey

          if (
            shortcut.key === e.key &&
            (!shortcut.requiresMod || modKey) &&
            (!shortcut.requiresShift || shiftKey) &&
            (!shortcut.requiresAlt || altKey)
          ) {
            // Check context
            if (
              shortcut.context === 'global' ||
              shortcut.context === currentContext ||
              shortcut.context === context
            ) {
              return shortcut
            }
          }
        }
      }

      return null
    },
    [context]
  )

  // Match sequence shortcuts (e.g., "g d")
  const matchSequence = useCallback(
    (sequence: string, currentContext: ContextType): KeyboardShortcut | null => {
      for (const shortcut of shortcuts) {
        if (
          shortcut.key === sequence &&
          !shortcut.requiresMod &&
          !shortcut.requiresShift &&
          !shortcut.requiresAlt
        ) {
          if (
            shortcut.context === 'global' ||
            shortcut.context === currentContext ||
            shortcut.context === context
          ) {
            return shortcut
          }
        }
      }
      return null
    },
    [context]
  )

  // Clear sequence buffer after timeout
  const clearSequenceBuffer = useCallback(() => {
    sequenceBuffer.current = []
    if (sequenceTimeout.current) {
      clearTimeout(sequenceTimeout.current)
    }
  }, [])

  // Handle keydown event
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled) return
      if (shouldIgnoreTarget(e.target)) return

      const currentContext = getCurrentContext()

      // Check for modifier shortcuts first
      const modShortcut = matchShortcut(e, currentContext)
      if (modShortcut) {
        e.preventDefault()
        e.stopPropagation()
        onShortcut(modShortcut.action)
        return
      }

      // Handle sequence shortcuts (non-modifier keys)
      if (!e.metaKey && !e.ctrlKey && !e.altKey && !e.shiftKey) {
        // Ignore special keys for sequences
        if (
          e.key.length === 1 ||
          e.key === 'ArrowUp' ||
          e.key === 'ArrowDown' ||
          e.key === 'ArrowLeft' ||
          e.key === 'ArrowRight' ||
          e.key === ' '
        ) {
          // Add key to sequence buffer
          sequenceBuffer.current.push(e.key)

          // Build sequence string
          const sequence = sequenceBuffer.current.join(' ')

          // Try to match sequence
          const seqShortcut = matchSequence(sequence, currentContext)
          if (seqShortcut) {
            e.preventDefault()
            e.stopPropagation()
            clearSequenceBuffer()
            onShortcut(seqShortcut.action)
            return
          }

          // Check if sequence could potentially match (for multi-key sequences)
          const couldMatch = shortcuts.some((s) => s.key.startsWith(sequence))

          if (!couldMatch) {
            // No potential match, clear buffer
            clearSequenceBuffer()

            // Check if single key matches
            const singleKeyShortcut = matchSequence(e.key, currentContext)
            if (singleKeyShortcut) {
              e.preventDefault()
              e.stopPropagation()
              onShortcut(singleKeyShortcut.action)
            }
          } else {
            // Potential match, wait for more keys
            e.preventDefault()
            if (sequenceTimeout.current) {
              clearTimeout(sequenceTimeout.current)
            }
            sequenceTimeout.current = setTimeout(clearSequenceBuffer, 1000)
          }
        }
      }
    },
    [
      enabled,
      shouldIgnoreTarget,
      getCurrentContext,
      matchShortcut,
      matchSequence,
      clearSequenceBuffer,
      onShortcut,
    ]
  )

  // Setup event listener
  useEffect(() => {
    if (!enabled) return

    window.addEventListener('keydown', handleKeyDown, true)

    return () => {
      window.removeEventListener('keydown', handleKeyDown, true)
      if (sequenceTimeout.current) {
        clearTimeout(sequenceTimeout.current)
      }
    }
  }, [enabled, handleKeyDown])

  return {
    clearSequenceBuffer,
  }
}

// Hook for listening to specific shortcuts
export function useShortcut(
  action: string,
  handler: () => void,
  options: { enabled?: boolean; context?: ContextType } = {}
) {
  const handleShortcut = useCallback(
    (triggeredAction: string) => {
      if (triggeredAction === action) {
        handler()
      }
    },
    [action, handler]
  )

  useKeyboard({
    enabled: options.enabled,
    context: options.context,
    onShortcut: handleShortcut,
  })
}
