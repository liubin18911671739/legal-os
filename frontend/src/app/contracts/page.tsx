'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { FileText, Trash2, Search, PlayCircle, Eye } from 'lucide-react'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'
import { useRouter } from 'next/navigation'

export default function ContractsPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await apiClient.getDocuments()
      setDocuments(response.items || [])
    } catch (error) {
      toast({
        title: 'Failed to load documents',
        description: error instanceof Error ? error.message : 'An error occurred',
        duration: 3000,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async (docId: string, fileName: string) => {
    try {
      // TODO: Read file content and call analysis API
      // For now, just show a toast
      toast({
        title: 'Analysis Feature',
        description: 'Full analysis integration coming soon. Please upload a new contract.',
      })
    } catch (error) {
      toast({
        title: 'Analysis Failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        duration: 5000,
      })
    }
  }

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this contract?')) {
      return
    }

    try {
      await apiClient.deleteDocument(docId)
      toast({
        title: 'Contract Deleted',
        description: 'The contract has been removed from the system',
      })
      loadDocuments()
    } catch (error) {
      toast({
        title: 'Deletion Failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        duration: 5000,
      })
    }
  }

  return (
    <div className="p-8">
      <Toaster />

      <h1 className="text-3xl font-bold mb-6">Contracts</h1>
      <p className="text-gray-600 mb-8">
        View and manage your uploaded contracts
      </p>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No contracts yet
          </h3>
          <p className="text-gray-600">
            Upload a contract to get started
          </p>
          <a
            href="/upload"
            className="inline-block mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Upload Contract
          </a>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <div className="relative flex items-center">
              <Search className="h-4 w-4 absolute left-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search contracts..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 hover:bg-gray-50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-gray-600" />
                  <div>
                    <h4 className="font-medium text-gray-900">{doc.title}</h4>
                    <div className="text-sm text-gray-600">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        doc.status === 'indexed' ? 'bg-green-100 text-green-800' :
                        doc.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {doc.status}
                      </span>
                      {' · '}
                      Type: {doc.file_type.toUpperCase()}
                      {doc.file_size && ` · ${doc.file_size}`}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleAnalyze(doc.id, doc.file_name)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Analyze"
                  >
                    <PlayCircle className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => router.push(`/report/${doc.id}`)}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="View Report"
                    disabled={doc.status !== 'indexed'}
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
