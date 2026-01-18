'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { Database, Search, Plus, Trash2, FileText } from 'lucide-react'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'

export default function KnowledgePage() {
  const { toast } = useToast()
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await apiClient.getDocuments()
      setDocuments(response.items || [])
    } catch (error) {
      toast({
        title: 'Failed to load knowledge base',
        description: error instanceof Error ? error.message : 'An error occurred',
        duration: 3000,
      })
    } finally {
      setLoading(false)
    }
  }

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="p-8">
      <Toaster />

      <h1 className="text-3xl font-bold mb-2">Knowledge Base</h1>
      <p className="text-gray-600 mb-8">
        Manage legal documents, regulations, and templates
      </p>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <>
          {/* Search and Actions */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6 flex items-center justify-between">
            <div className="relative flex items-center">
              <Search className="h-4 w-4 absolute left-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search knowledge base..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-96 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              <Plus className="h-4 w-4" />
              Upload Document
            </button>
          </div>

          {/* Documents List */}
          {filteredDocuments.length === 0 ? (
            <div className="text-center py-16 bg-gray-50 rounded-lg">
              <Database className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No documents found
              </h3>
              <p className="text-gray-600">
                Upload legal documents, regulations, or templates to get started
              </p>
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="divide-y divide-gray-200">
                {filteredDocuments.map((doc) => (
                  <div key={doc.id} className="p-4 hover:bg-gray-50 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-gray-600" />
                      <div>
                        <h4 className="font-medium text-gray-900">{doc.title}</h4>
                        <div className="text-sm text-gray-600">
                          {doc.file_name} · {doc.file_type.toUpperCase()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        doc.vectorized ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {doc.vectorized ? 'Indexed' : 'Pending'}
                      </span>
                      <Trash2 className="h-4 w-4 text-gray-400 hover:text-red-600 cursor-pointer" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
