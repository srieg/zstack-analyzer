import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { EyeIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { api } from '@/services/api'

export default function AnalysisResults() {
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('')

  const { data: images = [], isLoading } = useQuery({
    queryKey: ['images'],
    queryFn: () => api.getImages(),
  })

  const { data: algorithms = [] } = useQuery({
    queryKey: ['validation-algorithms'],
    queryFn: () => api.getValidationAlgorithms(),
  })

  // Get all results for all images
  const imageResults = useQuery({
    queryKey: ['all-results', images.map(img => img.id)],
    queryFn: async () => {
      const results = await Promise.all(
        images.map(async (image) => {
          const imageResults = await api.getAnalysisResults(image.id)
          return { image, results: imageResults }
        })
      )
      return results
    },
    enabled: images.length > 0,
  })

  const allResults = imageResults.data?.flatMap(({ image, results }) =>
    results.map(result => ({ ...result, image }))
  ) || []

  const filteredResults = selectedAlgorithm
    ? allResults.filter(result => result.algorithm_name === selectedAlgorithm)
    : allResults

  if (isLoading || imageResults.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
        <p className="mt-2 text-gray-600">
          View and manage all analysis results across your image collection
        </p>
      </div>

      {/* Summary Stats */}
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
              <p className="text-2xl font-bold text-gray-900">{allResults.length}</p>
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
              <p className="text-2xl font-bold text-gray-900">
                {allResults.filter(r => r.human_validated).length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <XCircleIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-gray-900">
                {allResults.filter(r => !r.human_validated).length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-purple-600 font-semibold text-sm">A</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Algorithms</p>
              <p className="text-2xl font-bold text-gray-900">{algorithms.length}</p>
            </div>
          </div>
        </div>
      </div>

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

      {/* Results Table */}
      <div className="card">
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Image
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Algorithm
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredResults.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No analysis results found
                  </td>
                </tr>
              ) : (
                filteredResults.map((result) => (
                  <tr key={result.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {result.image.filename}
                          </div>
                          <div className="text-sm text-gray-500">
                            {result.image.width}×{result.image.height}×{result.image.depth}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{result.algorithm_name}</div>
                      <div className="text-sm text-gray-500">v{result.algorithm_version}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {result.confidence_score ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {(result.confidence_score * 100).toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400">N/A</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          result.human_validated
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {result.human_validated ? 'Validated' : 'Pending'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(result.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link
                        to={`/images/${result.image.id}`}
                        className="text-primary-600 hover:text-primary-900 inline-flex items-center"
                      >
                        <EyeIcon className="h-4 w-4 mr-1" />
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}