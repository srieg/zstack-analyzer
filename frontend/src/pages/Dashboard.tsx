import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  CloudArrowUpIcon,
  EyeIcon,
  CheckCircleIcon,
  ChartBarIcon,
  CpuChipIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline'
import { api } from '@/services/api'
import { Card, Badge, Progress, Button } from '@/components/ui'

// Animated Stat Card Component
function StatCard({
  title,
  value,
  icon: Icon,
  color,
  trend,
  delay = 0,
}: {
  title: string
  value: number | string
  icon: any
  color: 'primary' | 'warning' | 'success' | 'secondary'
  trend?: { value: number; label: string }
  delay?: number
}) {
  const colorClasses = {
    primary: 'from-primary-500 to-primary-600',
    warning: 'from-warning-500 to-warning-600',
    success: 'from-success-500 to-success-600',
    secondary: 'from-secondary-500 to-secondary-600',
  }

  return (
    <Card
      variant="hover"
      className="relative overflow-hidden group"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Background gradient glow */}
      <div className={`absolute inset-0 bg-gradient-to-br ${colorClasses[color]} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />

      {/* Icon with gradient background */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
            {title}
          </p>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 transition-transform duration-200 group-hover:scale-105">
            {value}
          </p>
          {trend && (
            <div className="flex items-center mt-2 gap-1">
              <ArrowTrendingUpIcon className={`h-4 w-4 ${trend.value >= 0 ? 'text-success-500' : 'text-error-500'}`} />
              <span className={`text-sm font-medium ${trend.value >= 0 ? 'text-success-600' : 'text-error-600'}`}>
                {trend.value >= 0 ? '+' : ''}{trend.value}%
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">{trend.label}</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClasses[color]} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>

      {/* Sparkline placeholder area */}
      <div className="mt-4 h-12 flex items-end gap-1 opacity-30 group-hover:opacity-50 transition-opacity">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className={`flex-1 bg-gradient-to-t ${colorClasses[color]} rounded-t`}
            style={{ height: `${Math.random() * 100}%` }}
          />
        ))}
      </div>
    </Card>
  )
}

export default function Dashboard() {
  const { data: images = [], isLoading: imagesLoading } = useQuery({
    queryKey: ['images'],
    queryFn: () => api.getImages(),
  })

  const { data: validationStats, isLoading: statsLoading } = useQuery({
    queryKey: ['validation-stats'],
    queryFn: () => api.getValidationStats(),
  })

  const recentImages = images.slice(0, 5)
  const processingImages = images.filter(img => img.processing_status === 'processing')

  const isLoading = imagesLoading || statsLoading

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl font-bold text-gradient-scientific">
          Dashboard
        </h1>
        <p className="mt-2 text-lg text-gray-600 dark:text-gray-400">
          GPU-accelerated confocal microscopy Z-stack analysis platform
        </p>
      </div>

      {/* Stats Grid with Animated Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} loading />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Images"
            value={images.length}
            icon={EyeIcon}
            color="primary"
            trend={{ value: 12, label: 'this week' }}
            delay={0}
          />
          <StatCard
            title="Processing"
            value={processingImages.length}
            icon={CpuChipIcon}
            color="warning"
            delay={100}
          />
          <StatCard
            title="Validated"
            value={validationStats?.validated_results || 0}
            icon={CheckCircleIcon}
            color="success"
            trend={{ value: 8, label: 'this week' }}
            delay={200}
          />
          <StatCard
            title="Validation Rate"
            value={`${validationStats?.validation_rate || 0}%`}
            icon={ChartBarIcon}
            color="secondary"
            trend={{ value: 5, label: 'improvement' }}
            delay={300}
          />
        </div>
      )}

      {/* Processing Progress (if any) */}
      {processingImages.length > 0 && (
        <Card variant="glass" className="animate-slide-up border-l-4 border-warning-500">
          <div className="flex items-start gap-4">
            <CpuChipIcon className="h-6 w-6 text-warning-500 animate-pulse flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Active Processing
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {processingImages.length} image{processingImages.length !== 1 ? 's' : ''} currently being analyzed
              </p>
              <Progress value={65} variant="bar" color="warning" showValue />
            </div>
          </div>
        </Card>
      )}

      {/* Quick Actions and Recent Images Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Quick Actions */}
        <Card className="animate-slide-up" style={{ animationDelay: '100ms' }}>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Quick Actions
          </h3>
          <div className="space-y-3">
            <Link
              to="/upload"
              className="group flex items-center p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 hover:shadow-md transition-all duration-200"
            >
              <div className="flex-shrink-0 p-3 rounded-lg bg-primary-50 dark:bg-primary-900/20 group-hover:bg-primary-100 dark:group-hover:bg-primary-900/30 transition-colors">
                <CloudArrowUpIcon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div className="ml-4 flex-1">
                <p className="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                  Upload New Images
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Upload TIFF, CZI, ND2, or LSM files
                </p>
              </div>
            </Link>

            <Link
              to="/validation"
              className="group flex items-center p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-success-500 dark:hover:border-success-500 hover:shadow-md transition-all duration-200"
            >
              <div className="flex-shrink-0 p-3 rounded-lg bg-success-50 dark:bg-success-900/20 group-hover:bg-success-100 dark:group-hover:bg-success-900/30 transition-colors">
                <CheckCircleIcon className="h-6 w-6 text-success-600 dark:text-success-400" />
              </div>
              <div className="ml-4 flex-1">
                <p className="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-success-600 dark:group-hover:text-success-400 transition-colors">
                  Validation Queue
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {validationStats?.pending_validation || 0} result{validationStats?.pending_validation !== 1 ? 's' : ''} pending validation
                </p>
              </div>
              {(validationStats?.pending_validation || 0) > 0 && (
                <Badge variant="warning" dot>
                  {validationStats?.pending_validation}
                </Badge>
              )}
            </Link>
          </div>
        </Card>

        {/* Recent Images */}
        <Card className="animate-slide-up" style={{ animationDelay: '200ms' }}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Recent Images
            </h3>
            <Link to="/results">
              <Button variant="ghost" size="sm">
                View All
              </Button>
            </Link>
          </div>
          <div className="space-y-3">
            {recentImages.length > 0 ? (
              recentImages.map((image, index) => (
                <Link
                  key={image.id}
                  to={`/images/${image.id}`}
                  className="group flex items-center justify-between p-3 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 hover:shadow-sm transition-all duration-200"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 dark:text-gray-100 truncate group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                      {image.filename}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {image.width}×{image.height}×{image.depth} • {image.channels} channels
                    </p>
                  </div>
                  <Badge
                    variant={
                      image.processing_status === 'completed'
                        ? 'success'
                        : image.processing_status === 'processing'
                        ? 'warning'
                        : image.processing_status === 'failed'
                        ? 'error'
                        : 'gray'
                    }
                    dot
                  >
                    {image.processing_status}
                  </Badge>
                </Link>
              ))
            ) : (
              <div className="text-center py-8">
                <EyeIcon className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600 mb-3" />
                <p className="text-gray-500 dark:text-gray-400 mb-4">No images uploaded yet</p>
                <Link to="/upload">
                  <Button variant="primary" size="sm" icon={<CloudArrowUpIcon className="h-4 w-4" />}>
                    Upload Your First Image
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
