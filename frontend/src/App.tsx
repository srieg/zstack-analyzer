import { useState, useCallback } from 'react'
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import Landing from '@/pages/Landing'
import Dashboard from '@/pages/Dashboard'
import ImageUpload from '@/pages/ImageUpload'
import ImageViewer from '@/pages/ImageViewer'
import ValidationQueue from '@/pages/ValidationQueue'
import AnalysisResults from '@/pages/AnalysisResults'
import CommandPalette from '@/components/CommandPalette'
import KeyboardShortcutsModal from '@/components/KeyboardShortcutsModal'
import QuickActions from '@/components/QuickActions'
import { useKeyboard } from '@/hooks/useKeyboard'

function App() {
  const location = useLocation()
  const navigate = useNavigate()
  const isLandingPage = location.pathname === '/'

  const [showCommandPalette, setShowCommandPalette] = useState(false)
  const [showShortcutsModal, setShowShortcutsModal] = useState(false)

  // Global keyboard shortcut handler
  const handleGlobalShortcut = useCallback(
    (action: string) => {
      switch (action) {
        case 'command_palette':
          setShowCommandPalette(true)
          break
        case 'show_shortcuts':
          setShowShortcutsModal(true)
          break
        case 'new_upload':
          navigate('/upload')
          break
        case 'navigate_dashboard':
          navigate('/app')
          break
        case 'navigate_upload':
          navigate('/upload')
          break
        case 'navigate_validation':
          navigate('/validation')
          break
        case 'navigate_results':
          navigate('/results')
          break
      }
    },
    [navigate]
  )

  // Setup global keyboard shortcuts (disabled on landing page)
  useKeyboard({
    enabled: !isLandingPage,
    context: 'global',
    onShortcut: handleGlobalShortcut,
  })

  // Handle command execution from command palette
  const handleCommandPaletteAction = useCallback((action: string) => {
    // Most actions are handled by the command palette itself
    // This is for any custom actions that need app-level handling
    console.log('Command palette action:', action)
  }, [])

  return (
    <>
      {isLandingPage ? (
        <Routes>
          <Route path="/" element={<Landing />} />
        </Routes>
      ) : (
        <Layout>
          <Routes>
            <Route path="/app" element={<Dashboard />} />
            <Route path="/upload" element={<ImageUpload />} />
            <Route path="/images/:id" element={<ImageViewer />} />
            <Route path="/validation" element={<ValidationQueue />} />
            <Route path="/results" element={<AnalysisResults />} />
          </Routes>
        </Layout>
      )}

      {/* Global components (disabled on landing page) */}
      {!isLandingPage && (
        <>
          <CommandPalette
            isOpen={showCommandPalette}
            onClose={() => setShowCommandPalette(false)}
            onExecuteAction={handleCommandPaletteAction}
          />

          <KeyboardShortcutsModal
            isOpen={showShortcutsModal}
            onClose={() => setShowShortcutsModal(false)}
          />

          <QuickActions onShowShortcuts={() => setShowShortcutsModal(true)} />
        </>
      )}
    </>
  )
}

export default App