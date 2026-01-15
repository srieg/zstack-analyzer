import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { api } from '@/services/api'

export default function ValidationQueue() {
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('')
  const queryClient = useQueryClient()

  const { data: queue = [], isLoading } = useQuery({
    queryKey: ['validation-queue', selectedAlgorithm],
    queryFn: () => api.getValidationQueue(50, selectedAlgorithm || undefined),
  })

  const { data: algorithms = [] } = useQuery({
    queryKey: ['validation-algorithms'],
    queryFn: () => api.getValidationAlgorithms(),
  })

  const { data: stats } = useQuery({
    queryKey: ['validation-stats', selectedAlgorithm],
    queryFn: () => api.getValidationStats(selectedAlgorithm || undefined),
  })

  const validateMutation = useMutation({
    mutationFn: ({ resultId, validated, notes }: { 
      resultId: string
      validated: boolean
      notes?: string 
    }) => api.validateResult(resultId, { validated, notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['validation-queue'] })
      queryClient.invalidateQueries({ queryKey: ['validation-stats'] })
    },
  })

  const handleValidate = (resultId: string, validated: boolean, notes?: string) => {
    validateMutation.mutate({ resultId, validated, notes })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Validation Queue</h1>
        <p className="mt-2 text-gray-600">
          Review and validate analysis results from the AI algorithms
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-blue-600 font-semibold text-sm">T</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Results</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_results}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Validated</p>
                <p className="text-2xl font-bold text-gray-900">{stats.validated_results}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <span className="text-yellow-600 font-semibold text-sm">P</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pending</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pending_validation}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <span className="text-purple-600 font-semibold text-sm">%</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Rate</p>
                <p className="text-2xl font-bold text-gray-900">{stats.validation_rate}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <div className="flex items-center space-x-4">
          <label htmlFor="algorithm-filter" className="text-sm font-medium text-gray-700">
            Filter by algorithm:
          </label>
          <select
            id="algorithm-filter"
            value={selectedAlgorithm}
            onChange={(e) => setSelectedAlgorithm(e.target.value)}
            className="input max-w-xs"
          >
            <option value="">All algorithms</option>
            {algorithms.map((algorithm) => (
              <option key={algorithm} value={algorithm}>
                {algorithm}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Queue */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Pending Validation</h3>
        
        {queue.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No pending validations</h3>
            <p className="mt-1 text-sm text-gray-500">
              All results have been validated or no results are available.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {queue.map((result) => (
              <div key={result.id} className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h4 className="text-lg font-medium text-gray-900">
                        {result.algorithm_name}
                      </h4>
                      <span className="text-sm text-gray-500">
                        v{result.algorithm_version}
                      </span>
                      {result.confidence_score && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {(result.confidence_score * 100).toFixed(1)}% confidence
                        </span>
                      )}
                    </div>
                    
                    <p className="mt-1 text-sm text-gray-500">
                      Processed {new Date(result.created_at).toLocaleString()}
                      {result.gpu_device && ` • GPU: ${result.gpu_device}`}
                      • {result.processing_time_ms}ms
                    </p>

                    <div className="mt-4 bg-gray-50 rounded-lg p-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Results Summary</h5>
                      <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                        {JSON.stringify(result.results, null, 2)}
                      </pre>
                    </div>
                  </div>

                  <div className="ml-6 flex flex-col space-y-2">
                    <button
                      onClick={() => handleValidate(result.id, true)}
                      disabled={validateMutation.isPending}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                    >
                      <CheckCircleIcon className="h-4 w-4 mr-1" />
                      Approve
                    </button>
                    
                    <button
                      onClick={() => handleValidate(result.id, false, 'Rejected by human reviewer')}
                      disabled={validateMutation.isPending}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                    >
                      <XCircleIcon className="h-4 w-4 mr-1" />
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}