'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { FileText, Download, Trash2, Search } from 'lucide-react'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'

export default function ContractsPage() {
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
                      Status: {doc.status} · Type: {doc.file_type.toUpperCase()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Download className="h-4 w-4 text-gray-400 hover:text-gray-600 cursor-pointer" />
                  <Trash2 className="h-4 w-4 text-gray-400 hover:text-red-600 cursor-pointer" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
