import axios from 'axios'
import type { 
  ImageStack, 
  AnalysisResult, 
  ValidationStats, 
  AnalysisRequest, 
  ValidationRequest 
} from '@/types'

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

export const api = {
  // Images
  async uploadImage(file: File): Promise<{ message: string; image_stack: ImageStack }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getImages(): Promise<ImageStack[]> {
    const response = await apiClient.get('/images/')
    return response.data
  },

  async getImage(id: string): Promise<ImageStack> {
    const response = await apiClient.get(`/images/${id}`)
    return response.data
  },

  async deleteImage(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/images/${id}`)
    return response.data
  },

  // Analysis
  async analyzeImage(
    imageId: string, 
    request: AnalysisRequest
  ): Promise<{ message: string; image_id: string; algorithm: string; status: string }> {
    const response = await apiClient.post(`/analysis/${imageId}/analyze`, request)
    return response.data
  },

  async getAnalysisResults(imageId: string): Promise<AnalysisResult[]> {
    const response = await apiClient.get(`/analysis/${imageId}/results`)
    return response.data
  },

  async getAnalysisResult(resultId: string): Promise<AnalysisResult> {
    const response = await apiClient.get(`/analysis/results/${resultId}`)
    return response.data
  },

  async validateResult(
    resultId: string, 
    request: ValidationRequest
  ): Promise<{ message: string; result_id: string; validated: boolean }> {
    const response = await apiClient.put(`/analysis/results/${resultId}/validate`, request)
    return response.data
  },

  // Validation
  async getValidationQueue(
    limit = 50, 
    algorithm?: string
  ): Promise<AnalysisResult[]> {
    const params = new URLSearchParams()
    params.append('limit', limit.toString())
    if (algorithm) params.append('algorithm', algorithm)
    
    const response = await apiClient.get(`/validation/queue?${params}`)
    return response.data
  },

  async getValidationStats(algorithm?: string): Promise<ValidationStats> {
    const params = algorithm ? `?algorithm=${algorithm}` : ''
    const response = await apiClient.get(`/validation/stats${params}`)
    return response.data
  },

  async getValidationAlgorithms(): Promise<string[]> {
    const response = await apiClient.get('/validation/algorithms')
    return response.data
  },
}

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle authentication errors
      console.error('Authentication required')
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error:', error.response.data)
    }
    return Promise.reject(error)
  }
)