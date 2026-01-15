# Power User Guide - Z-Stack Microscopy Analyzer

Learn to use the analyzer like a pro with these workflows and productivity tips.

## Quick Start for Power Users

1. **Open Command Palette**: `Cmd+K` (or `Ctrl+K` on Windows/Linux)
2. **View All Shortcuts**: Press `?` key
3. **Navigate Fast**: Use `g` sequences (`g d` = dashboard, `g u` = upload, etc.)

## Common Workflows

### Workflow 1: Quick Image Upload and Analysis

```
1. Press 'n' → Opens upload page
2. Select/drop your Z-stack image
3. Wait for upload
4. Press 'g v' → View the image
5. Press 'a' → Run analysis
6. Press 'v' → Validate results
```

**Time saved**: ~30 seconds per image vs mouse clicking

### Workflow 2: Multi-Channel Inspection

```
1. Navigate to image viewer
2. Press '1' → View channel 1
3. Press ']' → Next Z-slice
4. Press '[' → Previous Z-slice
5. Press '2' → Switch to channel 2
6. Use mouse wheel → Scroll through slices
7. Press 'm' → Toggle MIP view
8. Press 'r' → Reset view
```

**Time saved**: ~45 seconds vs using UI controls

### Workflow 3: Validation Queue Processing

```
1. Press 'g v' → Go to validation queue
2. Click first result
3. Review in viewer
4. Press 'v' → Validate
5. Press 'g v' → Back to queue
6. Repeat
```

**Alternative with Command Palette**:
```
1. Cmd+K → Type "validation"
2. Enter → Go to validation
3. Process images
4. Cmd+K → Type "validate"
5. Enter → Validate current
```

### Workflow 4: Precise Slice Examination

```
1. In viewer, press 'f' → Fullscreen
2. Use '[' and ']' → Navigate slices
3. Press '+' → Zoom in
4. Arrow keys → Pan around
5. Right-click → Quick menu for analysis
6. Press 'r' → Reset when done
7. Press 'f' → Exit fullscreen
```

## Advanced Techniques

### The "G" Master Key

All navigation starts with `g` (for "go"):

- `g d` = Dashboard
- `g u` = Upload
- `g v` = Validation
- `g r` = Results
- `g i` = Images

**Pro tip**: Type these without pausing between keys. The system waits 1 second for the second key.

### Command Palette Mastery

The command palette (`Cmd+K`) supports fuzzy search:

- Type "val" → Matches "Validate", "Validation Queue"
- Type "ch 2" → Matches "Switch to Channel 2"
- Type "ana" → Matches "Run Analysis"

**Pro tip**: Recent actions appear at the top for quick access.

### Undo/Redo Everything

Every parameter change is tracked:

```
1. Press '2' → Switch to channel 2
2. Press '+' → Zoom in
3. Arrow Right → Pan right
4. Press 'm' → Toggle MIP

Now made a mistake?
5. Cmd+Z → Undo MIP toggle
6. Cmd+Z → Undo pan
7. Cmd+Z → Undo zoom
8. Cmd+Shift+Z → Redo zoom
```

**Pro tip**: The undo stack persists per image, so you can freely experiment.

### Context Menu Speed

Right-click on viewer to access:
- Quick actions with visual shortcuts
- One-click common operations
- Keyboard shortcuts displayed inline

**Pro tip**: Right-click to learn shortcuts, then use keyboard for speed.

### History Panel (Future Feature)

View all your recent actions:
- See what you changed
- Click to undo to that point
- Export action log for reproducibility

## Keyboard Shortcuts Cheat Sheet

### Essential (Memorize These First)

```
?              Show shortcuts
Cmd+K          Command palette
n              New upload
a              Run analysis
v              Validate
r              Reset view
f              Fullscreen
1-4            Switch channels
m              Toggle MIP
```

### Navigation

```
g d            Dashboard
g u            Upload
g v            Validation
g r            Results
```

### Z-Slice Navigation

```
[              Previous slice
]              Next slice
Mouse wheel    Scroll slices
```

### Zoom & Pan

```
+ or =         Zoom in
-              Zoom out
Arrow keys     Pan around
```

### System

```
Cmd+Z          Undo
Cmd+Shift+Z    Redo
Escape         Close dialogs
```

## Mobile Productivity

On tablets and phones:

1. **FAB Menu**: Tap the floating button (bottom-right)
2. **Quick Actions**: Access upload, analysis, validation
3. **Touch Gestures**:
   - Pinch to zoom
   - Two-finger drag to pan
   - Swipe up/down for slices (future)

## Productivity Metrics

### Time Savings Per Session

Average user without shortcuts:
- Navigate to page: 3-5 seconds
- Switch channels: 2-3 seconds
- Adjust view: 4-6 seconds
- Run analysis: 2-3 seconds

Power user with shortcuts:
- Navigate to page: <1 second
- Switch channels: <0.5 seconds
- Adjust view: 1-2 seconds
- Run analysis: <0.5 seconds

**Estimated time saved**: 40-60% reduction in UI interaction time

### Actions Per Minute

- Mouse-only user: ~20-30 actions/minute
- Keyboard power user: ~60-100 actions/minute
- Hybrid (keyboard + mouse): ~80-120 actions/minute

## Tips & Tricks

### 1. Chain Sequences

```bash
# Instead of:
Click Upload → Select file → Click back → Click image

# Do this:
n → (select file) → g i
```

### 2. Use Undo for Exploration

```bash
# Try different channels quickly:
1 → (view) → Cmd+Z → 2 → (view) → Cmd+Z → 3
```

### 3. Command Palette for Rare Actions

Don't memorize every shortcut. For infrequent actions, just:
```
Cmd+K → Type what you want → Enter
```

### 4. Right-Click to Learn

When you forget a shortcut:
1. Right-click
2. See the shortcut next to the action
3. Use keyboard next time

### 5. Fullscreen for Focus

```
f → (work in fullscreen) → f
```

Eliminates distractions during detailed analysis.

### 6. Reset Often

After zooming and panning, quickly reset with `r` instead of manually adjusting.

### 7. Mobile Quick Actions

On mobile, keep the FAB open while working:
- Tap once to expand
- Tap actions as needed
- Tap X to close

## Customization (Future)

Coming soon:
- Custom shortcut mapping
- Export/import configurations
- Per-project shortcuts
- Macro recording

## Accessibility Features

- **Visual Feedback**: All shortcuts show in UI
- **Screen Reader**: Announces shortcut actions
- **High Contrast**: Shortcut UI respects system theme
- **Keyboard-Only**: Entire app navigable without mouse

## Troubleshooting

### Shortcuts Not Working?

1. **Check context**: Some shortcuts only work in specific views
2. **Input focus**: Shortcuts disabled when typing in fields
3. **Browser conflict**: Some browsers override certain keys
4. **Command palette**: Use `Cmd+K` if a shortcut fails

### Finding the Right Shortcut?

1. Press `?` for full shortcut list
2. Use search in shortcuts modal
3. Try command palette (`Cmd+K`)
4. Right-click for context menu

### Undo Not Working?

1. Only certain actions can be undone (view changes, parameters)
2. Undo stack is per-image (cleared when changing images)
3. Check if action has history tracking (most do)

## Performance Optimization

For large Z-stacks (>100 slices):

1. Use keyboard for slice navigation (faster than slider)
2. Toggle between MIP and slice views with `m`
3. Use `[` and `]` for precise slice stepping
4. Fullscreen (`f`) for better performance

## Best Practices

1. **Learn incrementally**: Master 3-5 shortcuts per week
2. **Use command palette**: When you forget a shortcut
3. **Print cheat sheet**: Keep reference handy
4. **Practice sequences**: Navigation patterns become muscle memory
5. **Combine with mouse**: Hybrid approach is often fastest

## Getting Help

- Press `?` - Keyboard shortcuts modal
- Press `Cmd+K` - Command palette with search
- Right-click - Context menu with shortcuts
- Read `KEYBOARD_SHORTCUTS.md` - Complete reference

## Contributing Workflows

Have a workflow to share? Submit a PR with:
1. Workflow description
2. Key sequence
3. Time savings estimate
4. Use case/scenario

---

**Remember**: The goal isn't to memorize every shortcut, but to eliminate friction in your most common workflows. Start with navigation (`g` sequences) and viewer controls (`1-4`, `[`, `]`), then expand from there.

Happy analyzing! 🔬⚡
