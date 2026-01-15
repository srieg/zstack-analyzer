import { create } from 'zustand'

export interface HistoryAction {
  id: string
  timestamp: number
  description: string
  type: 'parameter_change' | 'view_change' | 'analysis' | 'validation' | 'other'
  data?: any
  undo?: () => void
  redo?: () => void
}

interface HistoryState {
  past: HistoryAction[]
  future: HistoryAction[]
  maxHistory: number

  // Actions
  addAction: (action: Omit<HistoryAction, 'id' | 'timestamp'>) => void
  undo: () => HistoryAction | null
  redo: () => HistoryAction | null
  clear: () => void
  canUndo: () => boolean
  canRedo: () => boolean
}

export const useHistory = create<HistoryState>((set, get) => ({
  past: [],
  future: [],
  maxHistory: 50,

  addAction: (action) => {
    const newAction: HistoryAction = {
      ...action,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
    }

    set((state) => ({
      past: [...state.past, newAction].slice(-state.maxHistory),
      future: [], // Clear redo stack when new action is added
    }))
  },

  undo: () => {
    const { past, future } = get()
    if (past.length === 0) return null

    const action = past[past.length - 1]
    const newPast = past.slice(0, -1)

    // Execute undo callback
    if (action.undo) {
      action.undo()
    }

    set({
      past: newPast,
      future: [action, ...future],
    })

    return action
  },

  redo: () => {
    const { past, future } = get()
    if (future.length === 0) return null

    const action = future[0]
    const newFuture = future.slice(1)

    // Execute redo callback
    if (action.redo) {
      action.redo()
    }

    set({
      past: [...past, action],
      future: newFuture,
    })

    return action
  },

  clear: () => {
    set({
      past: [],
      future: [],
    })
  },

  canUndo: () => get().past.length > 0,
  canRedo: () => get().future.length > 0,
}))

// Helper hook for tracking parameter changes
export function useParameterHistory<T>(
  paramName: string,
  currentValue: T,
  setValue: (value: T) => void
) {
  const { addAction } = useHistory()

  const updateParameter = (newValue: T) => {
    const oldValue = currentValue

    addAction({
      description: `Changed ${paramName}`,
      type: 'parameter_change',
      data: { paramName, oldValue, newValue },
      undo: () => setValue(oldValue),
      redo: () => setValue(newValue),
    })

    setValue(newValue)
  }

  return updateParameter
}

// Format action for display
export function formatHistoryAction(action: HistoryAction): string {
  const date = new Date(action.timestamp)
  const time = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })

  return `${time} - ${action.description}`
}

// Get history stats
export function getHistoryStats() {
  const { past, future } = useHistory.getState()

  const typeCount: Record<string, number> = {}
  past.forEach((action) => {
    typeCount[action.type] = (typeCount[action.type] || 0) + 1
  })

  return {
    totalActions: past.length,
    canUndo: past.length > 0,
    canRedo: future.length > 0,
    typeCount,
  }
}
