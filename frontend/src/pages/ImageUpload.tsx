import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { CloudArrowUpIcon } from '@heroicons/react/24/outline'
import { api } from '@/services/api'

export default function ImageUpload() {
  const [dragActive, setDragActive] = useState(false)
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.uploadImage(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images'] })
    },
  })

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    const allowedTypes = ['.tif', '.tiff', '.czi', '.nd2', '.lsm']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!allowedTypes.includes(fileExtension)) {
      alert('Please upload a supported file format: TIFF, CZI, ND2, or LSM')
      return
    }

    uploadMutation.mutate(file)
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Images</h1>
        <p className="mt-2 text-gray-600">
          Upload confocal microscopy Z-stack images for analysis
        </p>
      </div>

      <div className="card">
        <div
          className={`relative border-2 border-dashed rounded-lg p-12 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors duration-200 ${
            dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={handleChange}
            accept=".tif,.tiff,.czi,.nd2,.lsm"
            disabled={uploadMutation.isPending}
          />
          
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          
          <div className="mt-4">
            <p className="text-lg font-medium text-gray-900">
              {uploadMutation.isPending ? 'Uploading...' : 'Drop files here or click to browse'}
            </p>
            <p className="mt-2 text-sm text-gray-500">
              Supported formats: TIFF, CZI, ND2, LSM (max 2GB)
            </p>
          </div>

          {uploadMutation.isPending && (
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-primary-600 h-2 rounded-full animate-pulse w-1/2"></div>
              </div>
            </div>
          )}
        </div>

        {uploadMutation.isError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">
              Upload failed: {uploadMutation.error?.message || 'Unknown error'}
            </p>
          </div>
        )}

        {uploadMutation.isSuccess && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">
              File uploaded successfully! Processing metadata...
            </p>
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Supported File Formats</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-700">TIFF (.tif, .tiff) - Multi-page support</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-sm text-gray-700">CZI (.czi) - Carl Zeiss format</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-sm text-gray-700">ND2 (.nd2) - Nikon format</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-sm text-gray-700">LSM (.lsm) - Zeiss LSM format</span>
          </div>
        </div>
        <p className="mt-4 text-xs text-gray-500">
          Green: Fully supported • Yellow: Coming soon
        </p>
      </div>
    </div>
  )
}