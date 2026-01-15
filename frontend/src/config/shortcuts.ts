/**
 * Keyboard Shortcuts Configuration
 * Defines all keyboard shortcuts for the Z-stack microscopy analyzer
 */

export type ShortcutCategory = 'navigation' | 'actions' | 'viewer' | 'settings' | 'help'

export interface KeyboardShortcut {
  key: string
  description: string
  category: ShortcutCategory
  action: string
  context?: 'global' | 'viewer' | 'dashboard' | 'upload' | 'validation' | 'results'
  requiresMod?: boolean // Requires Cmd/Ctrl
  requiresShift?: boolean
  requiresAlt?: boolean
}

export const shortcuts: KeyboardShortcut[] = [
  // Navigation shortcuts
  {
    key: 'g d',
    description: 'Go to Dashboard',
    category: 'navigation',
    action: 'navigate_dashboard',
    context: 'global',
  },
  {
    key: 'g u',
    description: 'Go to Upload',
    category: 'navigation',
    action: 'navigate_upload',
    context: 'global',
  },
  {
    key: 'g v',
    description: 'Go to Validation',
    category: 'navigation',
    action: 'navigate_validation',
    context: 'global',
  },
  {
    key: 'g r',
    description: 'Go to Results',
    category: 'navigation',
    action: 'navigate_results',
    context: 'global',
  },
  {
    key: 'g i',
    description: 'Go to Images',
    category: 'navigation',
    action: 'navigate_images',
    context: 'global',
  },

  // Action shortcuts
  {
    key: 'n',
    description: 'New upload',
    category: 'actions',
    action: 'new_upload',
    context: 'global',
  },
  {
    key: 'a',
    description: 'Run analysis',
    category: 'actions',
    action: 'run_analysis',
    context: 'viewer',
  },
  {
    key: 'v',
    description: 'Validate current result',
    category: 'actions',
    action: 'validate_result',
    context: 'viewer',
  },
  {
    key: 'k',
    description: 'Command palette',
    category: 'actions',
    action: 'command_palette',
    context: 'global',
    requiresMod: true,
  },
  {
    key: 'z',
    description: 'Undo',
    category: 'actions',
    action: 'undo',
    context: 'global',
    requiresMod: true,
  },
  {
    key: 'z',
    description: 'Redo',
    category: 'actions',
    action: 'redo',
    context: 'global',
    requiresMod: true,
    requiresShift: true,
  },

  // Viewer controls
  {
    key: '1',
    description: 'Switch to Channel 1',
    category: 'viewer',
    action: 'channel_1',
    context: 'viewer',
  },
  {
    key: '2',
    description: 'Switch to Channel 2',
    category: 'viewer',
    action: 'channel_2',
    context: 'viewer',
  },
  {
    key: '3',
    description: 'Switch to Channel 3',
    category: 'viewer',
    action: 'channel_3',
    context: 'viewer',
  },
  {
    key: '4',
    description: 'Switch to Channel 4',
    category: 'viewer',
    action: 'channel_4',
    context: 'viewer',
  },
  {
    key: 'm',
    description: 'Toggle MIP view',
    category: 'viewer',
    action: 'toggle_mip',
    context: 'viewer',
  },
  {
    key: 's',
    description: 'Toggle slice view',
    category: 'viewer',
    action: 'toggle_slice',
    context: 'viewer',
  },
  {
    key: 'r',
    description: 'Reset view',
    category: 'viewer',
    action: 'reset_view',
    context: 'viewer',
  },
  {
    key: 'f',
    description: 'Toggle fullscreen',
    category: 'viewer',
    action: 'toggle_fullscreen',
    context: 'viewer',
  },
  {
    key: '=',
    description: 'Zoom in',
    category: 'viewer',
    action: 'zoom_in',
    context: 'viewer',
  },
  {
    key: '-',
    description: 'Zoom out',
    category: 'viewer',
    action: 'zoom_out',
    context: 'viewer',
  },
  {
    key: 'ArrowUp',
    description: 'Pan up',
    category: 'viewer',
    action: 'pan_up',
    context: 'viewer',
  },
  {
    key: 'ArrowDown',
    description: 'Pan down',
    category: 'viewer',
    action: 'pan_down',
    context: 'viewer',
  },
  {
    key: 'ArrowLeft',
    description: 'Pan left',
    category: 'viewer',
    action: 'pan_left',
    context: 'viewer',
  },
  {
    key: 'ArrowRight',
    description: 'Pan right',
    category: 'viewer',
    action: 'pan_right',
    context: 'viewer',
  },
  {
    key: ' ',
    description: 'Play/Pause (time series)',
    category: 'viewer',
    action: 'toggle_play',
    context: 'viewer',
  },
  {
    key: '[',
    description: 'Previous Z-slice',
    category: 'viewer',
    action: 'slice_prev',
    context: 'viewer',
  },
  {
    key: ']',
    description: 'Next Z-slice',
    category: 'viewer',
    action: 'slice_next',
    context: 'viewer',
  },

  // Help
  {
    key: '?',
    description: 'Show keyboard shortcuts',
    category: 'help',
    action: 'show_shortcuts',
    context: 'global',
  },
]

export const categoryLabels: Record<ShortcutCategory, string> = {
  navigation: 'Navigation',
  actions: 'Actions',
  viewer: 'Viewer Controls',
  settings: 'Settings',
  help: 'Help',
}

// Helper to format key combinations for display
export function formatShortcut(shortcut: KeyboardShortcut): string {
  const parts: string[] = []

  if (shortcut.requiresMod) {
    parts.push(isMac() ? '⌘' : 'Ctrl')
  }

  if (shortcut.requiresShift) {
    parts.push(isMac() ? '⇧' : 'Shift')
  }

  if (shortcut.requiresAlt) {
    parts.push(isMac() ? '⌥' : 'Alt')
  }

  parts.push(shortcut.key.toUpperCase())

  return parts.join(' + ')
}

export function isMac(): boolean {
  return typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0
}
