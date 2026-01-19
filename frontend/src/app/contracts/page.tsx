'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { FileText, Trash2, Search, PlayCircle, Eye, FileText as FileIcon, Plus } from 'lucide-react'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { zhCN } from '@/lib/translations'
import Link from 'next/link'

export default function ContractsPage() {
  const router = useRouter()
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
        title: '加载失败',
        description: error instanceof Error ? error.message : '发生错误',
        duration: 3000,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async (docId: string, fileName: string) => {
    try {
      toast({
        title: '分析功能',
        description: '完整分析功能即将推出，请上传新合同',
      })
    } catch (error) {
      toast({
        title: '分析失败',
        description: error instanceof Error ? error.message : '发生错误',
        duration: 5000,
      })
    }
  }

  const handleDelete = async (docId: string) => {
    if (!confirm(zhCN.alert.confirmDeleteMessage)) {
      return
    }

    try {
      await apiClient.deleteDocument(docId)
      toast({
        title: '合同已删除',
        description: '合同已从系统中移除',
      })
      loadDocuments()
    } catch (error) {
      toast({
        title: '删除失败',
        description: error instanceof Error ? error.message : '发生错误',
        duration: 5000,
      })
    }
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; variant: 'success' | 'warning' | 'secondary' }> = {
      indexed: { label: zhCN.status.completed, variant: 'success' },
      processing: { label: zhCN.status.processing, variant: 'warning' },
      uploaded: { label: zhCN.status.uploaded, variant: 'secondary' },
    }
    const statusInfo = statusMap[status] || { label: status, variant: 'secondary' }
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
  }

  const filteredDocs = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <Toaster />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {zhCN.contracts.title}
          </h1>
          <p className="text-gray-600 mt-1">
            {zhCN.contracts.description}
          </p>
        </div>
        <Link href="/upload">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            {zhCN.upload.title}
          </Button>
        </Link>
      </div>

      {loading ? (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      ) : documents.length === 0 ? (
        <Card>
          <CardContent className="py-16">
            <div className="flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center">
                <FileText className="h-10 w-10 text-gray-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {zhCN.empty.noContracts}
                </h3>
                <p className="text-gray-600 mb-4">
                  {zhCN.empty.noContractsDesc}
                </p>
                <Link href="/upload">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    {zhCN.empty.uploadNow}
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="text-sm text-gray-600">
                {filteredDocs.length} {zhCN.contracts.fileName}
              </div>
              <div className="relative w-72">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder={zhCN.contracts.searchPlaceholder}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{zhCN.contracts.fileName}</TableHead>
                  <TableHead>{zhCN.contracts.status}</TableHead>
                  <TableHead>{zhCN.common.type}</TableHead>
                  <TableHead>{zhCN.common.date}</TableHead>
                  <TableHead className="text-right">{zhCN.contracts.actions}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDocs.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FileIcon className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-gray-900 truncate">
                            {doc.title}
                          </p>
                          <p className="text-sm text-gray-500 truncate">
                            {doc.file_name}
                          </p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(doc.status)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{doc.file_type.toUpperCase()}</Badge>
                    </TableCell>
                    <TableCell>
                      {doc.file_size}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleAnalyze(doc.id, doc.file_name)}
                          className="hover:bg-blue-50 hover:text-blue-600"
                          title={zhCN.contracts.analyze}
                        >
                          <PlayCircle className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => router.push(`/report/${doc.id}`)}
                          disabled={doc.status !== 'indexed'}
                          className="hover:bg-green-50 hover:text-green-600 disabled:opacity-30"
                          title={zhCN.contracts.viewReport}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(doc.id)}
                          className="hover:bg-red-50 hover:text-red-600"
                          title={zhCN.common.delete}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
