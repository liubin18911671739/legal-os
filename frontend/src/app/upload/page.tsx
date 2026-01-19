'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { zhCN } from '@/lib/translations'
import { UploadCloud, FileText, Brain, ShieldCheck, FileCheck, X } from 'lucide-react'

export default function UploadPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    const validFiles = selectedFiles.filter(
      (file) => file.size <= 10 * 1024 * 1024
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

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)

    try {
      for (const file of files) {
        const document = await apiClient.createDocument({
          title: file.name.replace(/\.[^/.]+$/, ''),
          file_name: file.name,
          file_type: file.name.split('.').pop() as 'pdf' | 'docx' | 'txt',
          file_size: `${(file.size / 1024).toFixed(2)} KB`,
        })

        toast({
          title: zhCN.upload.uploadSuccess,
          description: `${file.name} ${zhCN.alert.uploadSuccess}`,
        })

        const fileText = await readFileContent(file)
        const contractType = detectContractType(file.name)
        const analysisResponse = await apiClient.analyzeContract({
          contract_id: document.id,
          contract_text: fileText,
          contract_type: contractType,
          user_query: 'Please analyze this contract for risks and compliance issues',
        })

        router.push(`/analysis/${analysisResponse.task_id}`)
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast({
        title: zhCN.upload.uploadError,
        description: error instanceof Error ? error.message : zhCN.alert.uploadFailed,
        duration: 5000,
      })
    } finally {
      setUploading(false)
    }
  }

  const readFileContent = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target?.result as string)
      reader.onerror = (e) => reject(new Error('Failed to read file'))
      reader.readAsText(file)
    })
  }

  const detectContractType = (fileName: string): 'employment' | 'sales' | 'lease' | 'service' | 'purchase' | 'other' => {
    const name = fileName.toLowerCase()
    if (name.includes('employment') || name.includes('contract') && name.includes('work')) return 'employment'
    if (name.includes('sales') || name.includes('purchase')) return 'sales'
    if (name.includes('lease')) return 'lease'
    if (name.includes('service')) return 'service'
    if (name.includes('purchase')) return 'purchase'
    return 'other'
  }

  const features = [
    {
      icon: Brain,
      title: 'AI 智能分析',
      description: '多智能体 RAG 系统深度分析合同条款',
    },
    {
      icon: ShieldCheck,
      title: '风险评估',
      description: '自动识别风险等级并提供改进建议',
    },
    {
      icon: FileCheck,
      title: '合规检查',
      description: '对照法律标准和企业政策进行验证',
    },
  ]

  return (
    <div className="space-y-8">
      <Toaster />

      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">
          {zhCN.upload.title}
        </h1>
        <p className="text-gray-600">
          {zhCN.upload.description}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className={`border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer ${
                  files.length > 0
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
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

                {uploading ? (
                  <div className="flex flex-col items-center gap-4">
                    <div className="h-16 w-16 border-4 border-t-blue-600 border-blue-200 rounded-full animate-spin" />
                    <div className="text-center space-y-2">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {zhCN.upload.analyzing}
                      </h3>
                      <p className="text-gray-600">
                        {zhCN.common.loading}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                      <UploadCloud className="h-8 w-8 text-gray-400" />
                    </div>
                    <div className="text-center space-y-2">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {zhCN.upload.dragDrop}
                      </h3>
                      <p className="text-gray-600">
                        {zhCN.upload.or} <span className="text-blue-600">{zhCN.upload.selectFiles}</span>
                      </p>
                      <div className="inline-flex items-center gap-2 text-sm text-gray-500 bg-white px-4 py-2 rounded-lg border border-gray-200">
                        <FileText className="h-4 w-4" />
                        {zhCN.upload.supportedFormats}
                      </div>
                      <div className="text-sm text-gray-500">
                        {zhCN.upload.maxSize}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {files.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  {zhCN.common.fileName} ({files.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <FileText className="h-5 w-5 text-gray-600 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    </div>
                    {!uploading && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeFile(index)}
                        className="flex-shrink-0 hover:bg-red-50 hover:text-red-600"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
                {uploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">{zhCN.common.loading}</span>
                      <span className="text-blue-600 font-medium">60%</span>
                    </div>
                    <Progress value={60} />
                  </div>
                )}
                <Button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="w-full"
                  size="lg"
                >
                  {uploading ? zhCN.upload.analyzing : zhCN.upload.uploadBtn}
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>功能特点</CardTitle>
              <CardDescription>
                系统将自动执行以下分析
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {features.map((feature) => {
                const Icon = feature.icon
                return (
                  <div key={feature.title} className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <Icon className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 text-sm mb-1">
                        {feature.title}
                      </h4>
                      <p className="text-xs text-gray-600">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                )
              })}
            </CardContent>
          </Card>

          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-gray-900 text-sm mb-2">
                    支持的文件类型
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">PDF</Badge>
                    <Badge variant="secondary">DOCX</Badge>
                    <Badge variant="secondary">TXT</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
