# Landing Page Components

Modern, animated landing page components for the Z-Stack Analyzer application.

## Components

### HeroAnimation

3D animated microscopy visualization using Three.js and React Three Fiber.

**Features:**
- Floating cell clusters with distortion effects
- Auto-rotating camera controls
- Grid plane background
- Responsive lighting system
- Optimized for performance

### StatsCounter

Animated numerical counters with intersection observer for scroll-triggered animations.

**Props:**
- `end: number` - Target number to count to
- `duration?: number` - Animation duration in milliseconds (default: 2000)
- `suffix?: string` - Text to append (e.g., "+", "%")
- `prefix?: string` - Text to prepend (e.g., "<", ">")
- `decimals?: number` - Decimal places (default: 0)
- `label: string` - Label text below counter

**Features:**
- Easing animation (ease-out-quart)
- Intersection observer triggers on scroll
- Glass morphism styling
- Hover scale effect

### FeatureCard

Animated feature cards with hover effects.

**Props:**
- `icon: ReactNode` - Icon element (typically Heroicon)
- `title: string` - Feature title
- `description: string` - Feature description
- `delay?: number` - Animation delay in seconds (for staggered entrance)

**Features:**
- Fade-in-up entrance animation
- Hover lift effect
- Gradient overlay on hover
- Rotating icon animation
- Animated arrow indicator

### TechStack

Infinite marquee carousel showcasing technology stack with tech icons.

**Features:**
- Auto-scrolling marquee animation
- Pause on hover
- Active item highlighting
- Fade edges for seamless loop
- Customizable tech list

### MobileNav

Mobile-responsive hamburger navigation menu.

**Features:**
- Smooth slide-in animation
- Backdrop blur overlay
- Touch-friendly interactions
- Auto-close on navigation
- Fixed positioning

## Usage

```tsx
import { Landing } from '@/pages/Landing'

// Landing page includes all components automatically
// Individual component usage:

import {
  HeroAnimation,
  StatsCounter,
  FeatureCard,
  TechStack,
  MobileNav
} from '@/components/landing'

// Example: StatsCounter
<StatsCounter
  end={100}
  suffix="+"
  label="Z-stacks/hour"
/>

// Example: FeatureCard
<FeatureCard
  icon={<CpuChipIcon className="w-8 h-8 text-white" />}
  title="GPU Processing"
  description="Blazing-fast inference..."
  delay={0.1}
/>
```

## Styling

All components use:
- Tailwind CSS for utility classes
- Custom animations with CSS keyframes
- Glass morphism effects
- Dark theme color palette (slate-900 background)

## Dependencies

- React 18.2+
- React Router DOM 6+
- Three.js 0.158+
- @react-three/fiber 8+
- @react-three/drei 9+
- @heroicons/react 2+
- Tailwind CSS 3+

## Customization

### Colors

Main gradient colors used:
- Blue: `from-blue-400 to-blue-600`
- Purple: `from-purple-400 to-purple-600`
- Pink: `from-pink-400 to-pink-600`

### Animations

Animation durations:
- Fast: 200-300ms (hover effects)
- Medium: 500-600ms (entrance animations)
- Slow: 2000-3000ms (counters, auto-rotate)

### Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## Performance Tips

1. The HeroAnimation uses `useFrame` hook which runs on every frame - keep logic minimal
2. StatsCounter uses IntersectionObserver to trigger only when visible
3. Marquee animation is GPU-accelerated via CSS transforms
4. All images/icons should be optimized for web

## Accessibility

- Semantic HTML structure
- Proper heading hierarchy (h1, h2, h3)
- ARIA labels where needed
- Keyboard navigation support
- Focus states on interactive elements
- Reduced motion support recommended (add to CSS)
