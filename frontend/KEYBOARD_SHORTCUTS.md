# Keyboard Shortcuts - Z-Stack Microscopy Analyzer

Power-user features that make researchers productive. Master these shortcuts to fly through the interface without touching your mouse.

## Quick Access

- **`?`** - Show keyboard shortcuts modal
- **`Cmd/Ctrl + K`** - Open command palette (fuzzy search all actions)

## Navigation Shortcuts

Navigate between pages with key sequences (press keys in order):

| Shortcut | Action |
|----------|--------|
| `g d` | Go to Dashboard |
| `g u` | Go to Upload |
| `g v` | Go to Validation Queue |
| `g r` | Go to Results |
| `g i` | Go to Images |

## Global Actions

Available from any page:

| Shortcut | Action |
|----------|--------|
| `n` | New upload |
| `Cmd/Ctrl + Z` | Undo last action |
| `Cmd/Ctrl + Shift + Z` | Redo action |

## Image Viewer Controls

These shortcuts are available when viewing an image:

### Analysis Actions

| Shortcut | Action |
|----------|--------|
| `a` | Run analysis |
| `v` | Validate current result |

### Channel Controls

| Shortcut | Action |
|----------|--------|
| `1` | Switch to Channel 1 |
| `2` | Switch to Channel 2 |
| `3` | Switch to Channel 3 |
| `4` | Switch to Channel 4 |

### View Controls

| Shortcut | Action |
|----------|--------|
| `m` | Toggle MIP (Maximum Intensity Projection) view |
| `s` | Toggle slice view |
| `r` | Reset view (zoom, pan, position) |
| `f` | Toggle fullscreen |

### Zoom & Pan

| Shortcut | Action |
|----------|--------|
| `+` or `=` | Zoom in |
| `-` | Zoom out |
| `Arrow Up` | Pan up |
| `Arrow Down` | Pan down |
| `Arrow Left` | Pan left |
| `Arrow Right` | Pan right |

### Z-Slice Navigation

| Shortcut | Action |
|----------|--------|
| `[` | Previous Z-slice |
| `]` | Next Z-slice |
| `Mouse Wheel` | Scroll through Z-slices |

### Time Series (when applicable)

| Shortcut | Action |
|----------|--------|
| `Space` | Play/Pause time series |

### Mouse Controls

- **Scroll Wheel** - Navigate through Z-slices
- **Right Click** - Open context menu with quick actions
- **Drag** (future) - Rotate in 3D mode
- **Double Click** (future) - Center view on point

## Command Palette

Press `Cmd/Ctrl + K` to open the command palette:

- **Fuzzy search** - Type to search all available actions
- **Recent actions** - Quick access to your most-used commands
- **Keyboard navigation** - Use arrow keys and Enter
- **Categories** - Actions organized by Navigation, Actions, Viewer, Settings, Help

### Command Palette Navigation

| Key | Action |
|-----|--------|
| `Arrow Down` | Next command |
| `Arrow Up` | Previous command |
| `Enter` | Execute selected command |
| `Escape` | Close palette |

## History & Undo System

Every parameter change, view adjustment, and action is tracked:

- **`Cmd/Ctrl + Z`** - Undo last change
- **`Cmd/Ctrl + Shift + Z`** - Redo change
- **Undo/Redo buttons** - Available in image viewer header

### What Can Be Undone?

- Channel switching
- Zoom and pan changes
- Slice navigation
- View mode toggles (MIP, slice view)
- Parameter adjustments
- View resets

## Context Menu

Right-click on the viewer for quick access to:

- Run Analysis (`A`)
- Validate Results (`V`)
- Reset View (`R`)
- Toggle Fullscreen (`F`)

Each menu item shows its keyboard shortcut for learning.

## Mobile Quick Actions

On mobile devices, a floating action button (FAB) provides quick access to:

- New Upload
- Run Analysis (when viewing)
- Validate (when viewing)
- Show Keyboard Shortcuts

Tap the FAB to expand the action menu.

## Tips for Power Users

1. **Learn sequences**: Navigation shortcuts use two-key sequences (like `g d`) - you don't need to hold them together
2. **Use the command palette**: When you forget a shortcut, `Cmd+K` is your friend
3. **Context awareness**: Different shortcuts are available in different views
4. **Undo freely**: Every action can be undone with `Cmd+Z`, so experiment without fear
5. **Right-click menus**: Show keyboard shortcuts inline for learning
6. **Mobile-first**: All features work on touch devices with the Quick Actions menu

## Implementation Details

### Context-Aware Shortcuts

The keyboard system automatically detects which page you're on and activates the appropriate shortcuts:

- **Global context** - Available everywhere (navigation, command palette)
- **Viewer context** - Image viewer specific (channels, zoom, slices)
- **Dashboard context** - Dashboard specific actions
- **Upload context** - Upload page actions
- **Validation context** - Validation queue actions

### Smart Input Detection

Shortcuts are disabled when typing in:
- Text inputs
- Textareas
- Content-editable elements
- Select dropdowns

This prevents conflicts between typing and shortcuts.

### Browser Conflict Prevention

The shortcut system:
- Uses capture phase to intercept events early
- Prevents default browser actions when needed
- Preserves critical browser shortcuts (Cmd+R, Cmd+W, etc.)
- Allows standard text editing shortcuts in input fields

## Accessibility

All keyboard shortcuts have visual indicators:
- Command palette shows shortcuts next to actions
- Context menus display shortcuts inline
- Shortcuts modal provides searchable reference
- Undo/redo buttons show keyboard hints on hover

## Contributing

To add new shortcuts:

1. Define in `/src/config/shortcuts.ts`
2. Add handler in appropriate component
3. Update this documentation
4. Test for conflicts with existing shortcuts

## Future Enhancements

Planned features:
- Custom shortcut configuration
- Shortcut recording/macros
- Per-project shortcut profiles
- Export/import shortcut configurations
