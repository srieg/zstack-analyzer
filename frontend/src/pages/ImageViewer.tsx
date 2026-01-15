import { useState, useCallback, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { useKeyboard } from '@/hooks/useKeyboard'
import ContextMenu, { useContextMenu, type ContextMenuItem } from '@/components/ContextMenu'
import { useHistory } from '@/stores/history'

interface ViewerState {
  currentChannel: number
  isMIPView: boolean
  isSliceView: boolean
  currentSlice: number
  zoom: number
  pan: { x: number; y: number }
  isFullscreen: boolean
  isPlaying: boolean
}

export default function ImageViewer() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const viewerRef = useRef<HTMLDivElement>(null)
  const { isOpen, position, handleContextMenu, closeMenu } = useContextMenu()
  const { addAction, undo, redo, canUndo, canRedo } = useHistory()

  // Viewer state
  const [viewerState, setViewerState] = useState<ViewerState>({
    currentChannel: 1,
    isMIPView: false,
    isSliceView: true,
    currentSlice: 0,
    zoom: 1,
    pan: { x: 0, y: 0 },
    isFullscreen: false,
    isPlaying: false,
  })

  const { data: image, isLoading, error } = useQuery({
    queryKey: ['image', id],
    queryFn: () => api.getImage(id!),
    enabled: !!id,
  })

  const { data: results = [] } = useQuery({
    queryKey: ['analysis-results', id],
    queryFn: () => api.getAnalysisResults(id!),
    enabled: !!id,
  })

  // Update parameter with history tracking
  const updateViewerState = <K extends keyof ViewerState>(
    key: K,
    value: ViewerState[K],
    description?: string
  ) => {
    const oldValue = viewerState[key]

    addAction({
      description: description || `Changed ${key}`,
      type: 'view_change',
      data: { key, oldValue, newValue: value },
      undo: () => setViewerState((s) => ({ ...s, [key]: oldValue })),
      redo: () => setViewerState((s) => ({ ...s, [key]: value })),
    })

    setViewerState((s) => ({ ...s, [key]: value }))
  }

  // Keyboard shortcut handlers
  const handleShortcut = useCallback(
    (action: string) => {
      switch (action) {
        // Navigation
        case 'navigate_dashboard':
          navigate('/')
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

        // Actions
        case 'run_analysis':
          handleRunAnalysis()
          break
        case 'validate_result':
          handleValidate()
          break
        case 'undo':
          undo()
          break
        case 'redo':
          redo()
          break

        // Channel switching
        case 'channel_1':
          updateViewerState('currentChannel', 1, 'Switched to Channel 1')
          break
        case 'channel_2':
          updateViewerState('currentChannel', 2, 'Switched to Channel 2')
          break
        case 'channel_3':
          updateViewerState('currentChannel', 3, 'Switched to Channel 3')
          break
        case 'channel_4':
          updateViewerState('currentChannel', 4, 'Switched to Channel 4')
          break

        // View controls
        case 'toggle_mip':
          updateViewerState('isMIPView', !viewerState.isMIPView, 'Toggled MIP view')
          break
        case 'toggle_slice':
          updateViewerState('isSliceView', !viewerState.isSliceView, 'Toggled slice view')
          break
        case 'reset_view':
          resetView()
          break
        case 'toggle_fullscreen':
          toggleFullscreen()
          break

        // Zoom and pan
        case 'zoom_in':
          updateViewerState('zoom', Math.min(viewerState.zoom + 0.1, 5), 'Zoomed in')
          break
        case 'zoom_out':
          updateViewerState('zoom', Math.max(viewerState.zoom - 0.1, 0.1), 'Zoomed out')
          break
        case 'pan_up':
          updateViewerState('pan', { ...viewerState.pan, y: viewerState.pan.y + 10 }, 'Panned up')
          break
        case 'pan_down':
          updateViewerState('pan', { ...viewerState.pan, y: viewerState.pan.y - 10 }, 'Panned down')
          break
        case 'pan_left':
          updateViewerState('pan', { ...viewerState.pan, x: viewerState.pan.x + 10 }, 'Panned left')
          break
        case 'pan_right':
          updateViewerState('pan', { ...viewerState.pan, x: viewerState.pan.x - 10 }, 'Panned right')
          break

        // Slice navigation
        case 'slice_prev':
          if (image && viewerState.currentSlice > 0) {
            updateViewerState('currentSlice', viewerState.currentSlice - 1, 'Previous slice')
          }
          break
        case 'slice_next':
          if (image && viewerState.currentSlice < image.depth - 1) {
            updateViewerState('currentSlice', viewerState.currentSlice + 1, 'Next slice')
          }
          break

        // Play/pause
        case 'toggle_play':
          updateViewerState('isPlaying', !viewerState.isPlaying, 'Toggled playback')
          break
      }
    },
    [navigate, viewerState, image, undo, redo]
  )

  // Setup keyboard shortcuts
  useKeyboard({
    enabled: true,
    context: 'viewer',
    onShortcut: handleShortcut,
  })

  // Handle mouse wheel for Z-slice navigation
  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
      if (!viewerRef.current?.contains(e.target as Node)) return
      if (!image) return

      e.preventDefault()

      const delta = e.deltaY > 0 ? 1 : -1
      const newSlice = Math.max(0, Math.min(image.depth - 1, viewerState.currentSlice + delta))

      if (newSlice !== viewerState.currentSlice) {
        updateViewerState('currentSlice', newSlice, `Scrolled to slice ${newSlice + 1}`)
      }
    }

    const viewer = viewerRef.current
    if (viewer) {
      viewer.addEventListener('wheel', handleWheel, { passive: false })
      return () => viewer.removeEventListener('wheel', handleWheel)
    }
  }, [image, viewerState.currentSlice])

  // Reset view
  const resetView = () => {
    addAction({
      description: 'Reset view',
      type: 'view_change',
      data: { oldState: viewerState },
      undo: () => setViewerState(viewerState),
      redo: () =>
        setViewerState({
          ...viewerState,
          zoom: 1,
          pan: { x: 0, y: 0 },
          currentSlice: 0,
        }),
    })

    setViewerState((s) => ({
      ...s,
      zoom: 1,
      pan: { x: 0, y: 0 },
      currentSlice: 0,
    }))
  }

  // Toggle fullscreen
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      viewerRef.current?.requestFullscreen()
      updateViewerState('isFullscreen', true, 'Entered fullscreen')
    } else {
      document.exitFullscreen()
      updateViewerState('isFullscreen', false, 'Exited fullscreen')
    }
  }

  // Handle actions
  const handleRunAnalysis = () => {
    console.log('Running analysis...')
    addAction({
      description: 'Started analysis',
      type: 'analysis',
    })
  }

  const handleValidate = () => {
    console.log('Validating results...')
    addAction({
      description: 'Validated results',
      type: 'validation',
    })
  }

  // Context menu items
  const contextMenuItems: ContextMenuItem[] = [
    {
      id: 'run-analysis',
      label: 'Run Analysis',
      shortcut: 'A',
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      onClick: handleRunAnalysis,
    },
    {
      id: 'validate',
      label: 'Validate Results',
      shortcut: 'V',
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      onClick: handleValidate,
    },
    { id: 'sep1', separator: true },
    {
      id: 'reset-view',
      label: 'Reset View',
      shortcut: 'R',
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      ),
      onClick: resetView,
    },
    {
      id: 'fullscreen',
      label: viewerState.isFullscreen ? 'Exit Fullscreen' : 'Fullscreen',
      shortcut: 'F',
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
      ),
      onClick: toggleFullscreen,
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !image) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Image not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{image.filename}</h1>
          <p className="mt-2 text-gray-600">
            Uploaded {new Date(image.upload_date).toLocaleDateString()}
          </p>
        </div>

        {/* History controls */}
        <div className="flex gap-2">
          <button
            onClick={() => undo()}
            disabled={!canUndo()}
            className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Undo (Cmd+Z)"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
          </button>
          <button
            onClick={() => redo()}
            disabled={!canRedo()}
            className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Redo (Cmd+Shift+Z)"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 10h-10a8 8 0 00-8 8v2M21 10l-6 6m6-6l-6-6" />
            </svg>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Image Preview */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">3D Viewer</h3>
              <div className="flex gap-2">
                {/* Channel switcher */}
                {[1, 2, 3, 4].slice(0, image.channels).map((ch) => (
                  <button
                    key={ch}
                    onClick={() => updateViewerState('currentChannel', ch, `Switched to Channel ${ch}`)}
                    className={`px-3 py-1 text-sm rounded ${
                      viewerState.currentChannel === ch
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {ch}
                  </button>
                ))}
              </div>
            </div>

            <div
              ref={viewerRef}
              onContextMenu={handleContextMenu}
              className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center relative cursor-crosshair"
              style={{
                transform: `scale(${viewerState.zoom}) translate(${viewerState.pan.x}px, ${viewerState.pan.y}px)`,
              }}
            >
              <div className="text-center">
                <p className="text-gray-500 mb-2">3D visualization will be implemented here</p>
                <p className="text-sm text-gray-400">
                  Channel {viewerState.currentChannel} • Slice {viewerState.currentSlice + 1}/{image.depth}
                </p>
                <p className="text-sm text-gray-400 mt-2">
                  {viewerState.isMIPView ? 'MIP View' : 'Slice View'} • Zoom: {(viewerState.zoom * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-gray-400 mt-4">
                  Right-click for options • Scroll to change slices
                </p>
              </div>
            </div>

            {/* Slice slider */}
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Z-Slice: {viewerState.currentSlice + 1} / {image.depth}
              </label>
              <input
                type="range"
                min={0}
                max={image.depth - 1}
                value={viewerState.currentSlice}
                onChange={(e) => updateViewerState('currentSlice', parseInt(e.target.value), `Changed to slice ${parseInt(e.target.value) + 1}`)}
                className="w-full"
              />
            </div>
          </div>
        </div>

        {/* Metadata and Controls */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Image Properties</h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Dimensions</dt>
                <dd className="text-sm text-gray-900">
                  {image.width} × {image.height} × {image.depth}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Channels</dt>
                <dd className="text-sm text-gray-900">{image.channels}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Bit Depth</dt>
                <dd className="text-sm text-gray-900">{image.bit_depth}-bit</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">File Size</dt>
                <dd className="text-sm text-gray-900">
                  {(image.file_size / 1024 / 1024).toFixed(1)} MB
                </dd>
              </div>
              {image.pixel_size_x && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Pixel Size</dt>
                  <dd className="text-sm text-gray-900">
                    {image.pixel_size_x.toFixed(3)} × {image.pixel_size_y?.toFixed(3)} × {image.pixel_size_z?.toFixed(3)} μm
                  </dd>
                </div>
              )}
            </dl>
          </div>

          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Status</h3>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                image.processing_status === 'completed'
                  ? 'bg-green-100 text-green-800'
                  : image.processing_status === 'processing'
                  ? 'bg-yellow-100 text-yellow-800'
                  : image.processing_status === 'failed'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {image.processing_status}
            </span>
          </div>

          {results.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Results</h3>
              <div className="space-y-3">
                {results.map((result) => (
                  <div key={result.id} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">
                        {result.algorithm_name}
                      </span>
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          result.human_validated
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {result.human_validated ? 'Validated' : 'Pending'}
                      </span>
                    </div>
                    {result.confidence_score && (
                      <p className="text-xs text-gray-500 mt-1">
                        Confidence: {(result.confidence_score * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Context Menu */}
      <ContextMenu
        items={contextMenuItems}
        isOpen={isOpen}
        position={position}
        onClose={closeMenu}
      />
    </div>
  )
}
