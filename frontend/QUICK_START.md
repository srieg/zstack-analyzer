# Z-Stack Analyzer UI - Quick Start Guide

## Getting Started

### 1. Install Dependencies
```bash
cd /Users/samriegel/zstack-analyzer/frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

---

## Key Features Tour

### Dark Mode
- **Toggle:** Click the moon/sun icon in sidebar (bottom)
- **Keyboard:** No shortcut yet (can add one)
- **Auto-detect:** System preference on first load
- **Persistent:** Saved to localStorage

### Command Palette
- **Keyboard:** `Cmd+K` (Mac) or `Ctrl+K` (Windows/Linux)
- **Features:** Quick navigation to all pages
- **Close:** Press `ESC` or click outside
- **Search:** Type to filter (not yet implemented, shows all pages)

### Collapsible Sidebar
- **Toggle:** Click X icon in top-right of sidebar
- **Collapsed Mode:** Shows icons only, hover for tooltips
- **Width:** 256px expanded, 80px collapsed
- **Smooth transition:** 300ms animation

### Breadcrumbs
- **Location:** Top header (sticky)
- **Auto-generated:** Based on current route
- **Clickable:** Navigate to parent pages
- **Styling:** Glass-morphism effect

### Status Bar
- **Location:** Below breadcrumbs
- **GPU Status:** Shows "Ready" with pulse animation
- **Processing Count:** Shows active processing jobs
- **System Status:** Overall system health indicator

---

## Component Library Usage

### Import Components
```tsx
import { Button, Card, Badge, Input, Progress, Modal, Tabs, Select, Slider } from '@/components/ui'
```

### Button Examples
```tsx
// Primary button
<Button variant="primary">Save Changes</Button>

// With loading state
<Button variant="primary" loading={isLoading}>Processing...</Button>

// With icon
<Button variant="secondary" icon={<CloudIcon className="h-4 w-4" />}>
  Upload
</Button>

// Danger button
<Button variant="danger">Delete</Button>

// Ghost button (transparent)
<Button variant="ghost">Cancel</Button>

// Full width
<Button variant="primary" fullWidth>Submit</Button>
```

### Card Examples
```tsx
// Standard card
<Card>
  <h3>Card Title</h3>
  <p>Card content here</p>
</Card>

// Hover effect card (lifts on hover)
<Card variant="hover">
  Interactive content
</Card>

// Glass-morphism card
<Card variant="glass">
  Translucent content
</Card>

// Loading state
<Card loading />

// Custom padding
<Card padding="lg">
  Extra padded content
</Card>
```

### Badge Examples
```tsx
<Badge variant="success">Completed</Badge>
<Badge variant="warning">Processing</Badge>
<Badge variant="error">Failed</Badge>
<Badge variant="primary" dot>5 pending</Badge>
```

### Input Examples
```tsx
// Basic input
<Input placeholder="Enter text..." />

// With label
<Input label="Email" type="email" />

// With error
<Input
  label="Password"
  type="password"
  error="Password must be at least 8 characters"
/>

// With success
<Input
  label="Username"
  success="Username is available"
/>

// With icon
<Input
  label="Search"
  icon={<MagnifyingGlassIcon className="h-5 w-5" />}
  iconPosition="left"
/>
```

### Progress Examples
```tsx
// Bar progress
<Progress value={65} variant="bar" showValue />

// Ring progress
<Progress value={75} variant="ring" size="lg" showValue />

// Steps progress
<Progress value={2} max={4} variant="steps" steps={4} />

// Color variants
<Progress value={50} color="success" />
<Progress value={80} color="warning" />
```

### Modal Examples
```tsx
const [open, setOpen] = useState(false)

<Modal
  open={open}
  onClose={() => setOpen(false)}
  title="Confirm Action"
  size="md"
>
  <p>Are you sure you want to proceed?</p>
  <div slot="footer">
    <Button variant="ghost" onClick={() => setOpen(false)}>
      Cancel
    </Button>
    <Button variant="danger" onClick={handleDelete}>
      Delete
    </Button>
  </div>
</Modal>
```

### Tabs Examples
```tsx
<Tabs
  tabs={[
    { id: 'overview', label: 'Overview', content: <OverviewTab /> },
    { id: 'settings', label: 'Settings', content: <SettingsTab />, icon: <CogIcon /> },
    { id: 'disabled', label: 'Disabled', content: null, disabled: true }
  ]}
  variant="line"
  defaultTab="overview"
  onChange={(tabId) => console.log('Tab changed:', tabId)}
/>
```

### Select Examples
```tsx
<Select
  label="Choose option"
  options={[
    { value: '1', label: 'Option 1' },
    { value: '2', label: 'Option 2', icon: <StarIcon /> },
    { value: '3', label: 'Disabled', disabled: true }
  ]}
  value={selectedValue}
  onChange={setSelectedValue}
/>
```

### Slider Examples
```tsx
<Slider
  label="Brightness"
  min={0}
  max={100}
  step={1}
  value={brightness}
  onChange={setBrightness}
  showValue
  unit="%"
  color="primary"
/>
```

---

## Styling Guidelines

### Colors
Use semantic color classes:
- **Primary:** `text-primary-600`, `bg-primary-500`
- **Success:** `text-success-600`, `bg-success-500`
- **Warning:** `text-warning-600`, `bg-warning-500`
- **Error:** `text-error-600`, `bg-error-500`
- **Gray scale:** `text-gray-500`, `bg-gray-100`

### Animations
Apply built-in animation classes:
- `animate-fade-in` - Fade in (0.5s)
- `animate-slide-up` - Slide up from bottom (0.5s)
- `animate-scale-in` - Scale from 95% to 100% (0.2s)
- `animate-pulse-glow` - Pulsing glow effect (2s infinite)

### Glass-morphism
Use utility classes:
- `glass` - Standard glass effect
- `glass-strong` - Stronger blur and opacity

### Gradients
- `bg-gradient-scientific` - Teal to purple gradient
- `text-gradient-scientific` - Gradient text effect

---

## Dark Mode Development

### Testing Dark Mode
1. Toggle dark mode in sidebar
2. Check all components in both modes
3. Verify color contrast
4. Test glass-morphism effects

### Adding Dark Mode Support
Use Tailwind's `dark:` prefix:
```tsx
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
  Content adapts to theme
</div>
```

---

## Animation Best Practices

### Staggered Animations
```tsx
{items.map((item, index) => (
  <div
    key={item.id}
    className="animate-fade-in"
    style={{ animationDelay: `${index * 100}ms` }}
  >
    {item.content}
  </div>
))}
```

### Conditional Animations
```tsx
<div className={clsx(
  isVisible && 'animate-slide-up',
  isHighlighted && 'animate-pulse-glow'
)}>
  Content
</div>
```

---

## Common Patterns

### Loading State
```tsx
{isLoading ? (
  <Card loading />
) : (
  <Card>
    {content}
  </Card>
)}
```

### Empty State
```tsx
{items.length === 0 ? (
  <div className="text-center py-12">
    <Icon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
    <p className="text-gray-500 mb-4">No items found</p>
    <Button variant="primary">Add First Item</Button>
  </div>
) : (
  <ItemList items={items} />
)}
```

### Stat Card Pattern (from Dashboard)
```tsx
<Card variant="hover" className="group relative overflow-hidden">
  <div className="flex items-start justify-between">
    <div className="flex-1">
      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
        {title}
      </p>
      <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">
        {value}
      </p>
    </div>
    <div className="p-3 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 shadow-lg">
      <Icon className="h-6 w-6 text-white" />
    </div>
  </div>
</Card>
```

---

## Performance Tips

### Avoid Inline Styles
❌ Bad:
```tsx
<div style={{ backgroundColor: 'red' }}>
```

✅ Good:
```tsx
<div className="bg-error-500">
```

### Use Tailwind Classes
- Smaller bundle size
- Better caching
- Consistent design

### Optimize Animations
- Use `transform` and `opacity` (GPU accelerated)
- Avoid animating `width`, `height`, `top`, `left`

---

## Troubleshooting

### Dark Mode Not Working
1. Check `localStorage.getItem('darkMode')`
2. Verify `document.documentElement` has `dark` class
3. Ensure dark mode is initialized in Layout.tsx

### Animations Not Showing
1. Check Tailwind config includes custom animations
2. Verify keyframes are defined in tailwind.config.js
3. Check for conflicting CSS

### Components Not Importing
1. Ensure path alias `@/components/ui` is configured in tsconfig.json
2. Check import statement syntax
3. Verify component files exist

### Styling Issues
1. Run `npm run build` to regenerate CSS
2. Clear browser cache
3. Check for conflicting global styles

---

## Next Development Steps

### To Update Other Pages:
1. Import UI components: `import { Card, Button, ... } from '@/components/ui'`
2. Replace old card divs with `<Card>` component
3. Replace buttons with `<Button>` component with variants
4. Add loading states with `<Card loading />` or `<Button loading />`
5. Add animations with `animate-*` classes
6. Test in both light and dark modes

### Example Migration (ImageUpload.tsx):
```tsx
// Before
<div className="card">
  <button className="btn-primary">Upload</button>
</div>

// After
<Card variant="hover" className="animate-fade-in">
  <Button variant="primary" icon={<CloudIcon />} loading={isUploading}>
    Upload
  </Button>
</Card>
```

---

**Need Help?** Check `UI_IMPROVEMENTS.md` for comprehensive documentation.
