'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react'

export default function UploadPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(false)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    const validFiles = selectedFiles.filter(
      (file) => file.size <= 10 * 1024 * 1024 // 10MB limit
    )
    setFiles(validFiles)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const droppedFiles = Array.from(e.dataTransfer.files || [])
    const validFiles = droppedFiles.filter(
      (file) => file.size <= 10 * 1024 * 1024
    )
    setFiles(validFiles)
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)

    try {
      for (const file of files) {
        const formData = new FormData()
        formData.append('file', file)

        // Create document record first
        const document = await apiClient.createDocument({
          title: file.name.replace(/\.[^/.]+$/, ''),
          file_name: file.name,
          file_type: file.name.split('.').pop() as 'pdf' | 'docx' | 'txt',
          file_size: `${(file.size / 1024).toFixed(2)} KB`,
        })

        toast({
          title: 'File uploaded successfully',
          description: `${file.name} has been added to the system`,
        })

        console.log('Created document:', document)
      }

      setUploaded(true)
      toast({
        title: 'Upload completed',
        description: `${files.length} file(s) uploaded successfully`,
        duration: 3000,
      })

      // Navigate to contracts page after delay
      setTimeout(() => {
        router.push('/contracts')
      }, 1500)
    } catch (error) {
      console.error('Upload error:', error)
      toast({
        title: 'Upload failed',
        description: error instanceof Error ? error.message : 'An error occurred during upload',
        duration: 5000,
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="p-8">
      <Toaster />

      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Upload Contract</h1>
        <p className="text-gray-600 mb-8">
          Upload your contract documents for AI-powered analysis
        </p>

        {/* Upload Area */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer ${
            files.length > 0
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400 bg-gray-50'
          } ${uploading ? 'pointer-events-none opacity-50' : 'hover:bg-gray-100'}`}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={handleFileSelect}
            className="hidden"
            disabled={uploading}
          />

          {uploaded ? (
            <div className="flex flex-col items-center gap-4">
              <CheckCircle2 className="h-16 w-16 text-green-500" />
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-1">
                  Upload Complete!
                </h3>
                <p className="text-gray-600">
                  Redirecting to contracts page...
                </p>
              </div>
            </div>
          ) : uploading ? (
            <div className="flex flex-col items-center gap-4">
              <div className="h-16 w-16 border-4 border-t-blue-600 border-blue-200 rounded-full animate-spin" />
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-1">
                  Uploading...
                </h3>
                <p className="text-gray-600">
                  Please wait while we process your files
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <UploadCloud className="h-16 w-16 text-gray-400" />
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Drag & Drop Files Here
                </h3>
                <p className="text-gray-600 mb-4">
                  Or click to browse files
                </p>
                <div className="text-sm text-gray-500">
                  <FileText className="inline h-4 w-4 mr-2" />
                  Supports PDF, DOCX, TXT files up to 10MB each
                </div>
              </div>
            </div>
          )}
        </div>

        {/* File List */}
        {files.length > 0 && !uploaded && (
          <div className="mt-8 bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">
              Selected Files ({files.length})
            </h3>
            <div className="space-y-2">
              {files.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-gray-600" />
                    <span className="text-sm font-medium text-gray-900">
                      {file.name}
                    </span>
                  </div>
                  <span className="text-sm text-gray-600">
                    {(file.size / 1024).toFixed(2)} KB
                  </span>
                </div>
              ))}
            </div>

            <button
              onClick={handleUpload}
              disabled={uploading}
              className="mt-6 w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? 'Uploading...' : 'Upload & Analyze'}
            </button>
          </div>
        )}

        {/* Info Cards */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h4 className="font-semibold text-gray-900 mb-2">AI Analysis</h4>
            <p className="text-sm text-gray-600">
              Contracts are analyzed using multi-agent RAG system
            </p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h4 className="font-semibold text-gray-900 mb-2">Risk Assessment</h4>
            <p className="text-sm text-gray-600">
              Automatic risk level detection with suggestions
            </p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h4 className="font-semibold text-gray-900 mb-2">Compliance Check</h4>
            <p className="text-sm text-gray-600">
              Verify against legal standards and company policies
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
