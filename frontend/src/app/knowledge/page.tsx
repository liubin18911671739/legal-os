'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { Database, Search, Plus, Trash2, FileText, Upload } from 'lucide-react'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'

interface SearchResult {
  document_id: string
  content: string
  score: number
  metadata?: {
    chunk_id: string
    file_name: string
  }
}

export default function KnowledgePage() {
  const { toast } = useToast()
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showSearchResults, setShowSearchResults] = useState(false)

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

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setShowSearchResults(false)
      return
    }

    setIsSearching(true)
    setShowSearchResults(true)

    try {
      // TODO: Call actual search API
      // For now, simulate search results
      const mockResults: SearchResult[] = documents
        .filter(doc =>
          doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
        )
        .map(doc => ({
          document_id: doc.id,
          content: `Sample content matching "${searchQuery}"...`,
          score: Math.random() * 0.3 + 0.7,
          metadata: {
            chunk_id: `chunk_${doc.id}`,
            file_name: doc.file_name,
          },
        }))
        .sort((a, b) => b.score - a.score)

      setSearchResults(mockResults.slice(0, 5))
    } catch (error) {
      toast({
        title: 'Search failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        duration: 3000,
      })
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

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
          {/* Search Bar */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
            <div className="flex items-center gap-4">
              <div className="relative flex-1">
                <Search className="h-5 w-5 absolute left-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search knowledge base..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pl-12 pr-4 py-3 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          {/* Search Results */}
          {showSearchResults && (
            <div className="bg-white rounded-lg border border-gray-200 mb-6">
              <h2 className="text-lg font-semibold p-4 border-b border-gray-200">
                Search Results ({searchResults.length})
              </h2>
              {searchResults.length === 0 ? (
                <div className="p-8 text-center text-gray-600">
                  No results found for "{searchQuery}"
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {searchResults.map((result, index) => (
                    <div key={index} className="p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-sm font-medium text-gray-900">
                              {result.metadata?.file_name || `Document ${result.document_id}`}
                            </span>
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                              Score: {result.score.toFixed(3)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {result.content}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Documents List */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-lg font-semibold">
                Documents ({documents.length})
              </h2>
              <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                <Upload className="h-4 w-4" />
                Upload Document
              </button>
            </div>
            {documents.length === 0 ? (
              <div className="text-center py-16 bg-gray-50">
                <Database className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No documents found
                </h3>
                <p className="text-gray-600">
                  Upload legal documents, regulations, or templates to get started
                </p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-4 hover:bg-gray-50 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-gray-600" />
                      <div>
                        <h4 className="font-medium text-gray-900">{doc.title}</h4>
                        <div className="text-sm text-gray-600">
                          {doc.file_name} · {doc.file_type.toUpperCase()} · {(doc.file_size || '0')}
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
            )}
          </div>
        </>
      )}
    </div>
  )
}
