'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'
import { Loader2, AlertTriangle, CheckCircle2, XCircle, FileText, Download, Share2, Printer, ArrowLeft } from 'lucide-react'

export default function ReportPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'summary' | 'findings' | 'suggestions'>('summary')
  const taskId = params.id as string

  useEffect(() => {
    if (!taskId) {
      setError('Task ID is required')
      setLoading(false)
      return
    }

    fetchAnalysisResult()
  }, [taskId])

  const fetchAnalysisResult = async () => {
    try {
      const result = await apiClient.getContractAnalysis(taskId)
      setAnalysis(result)
      setLoading(false)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch analysis result:', err)
      setError(err instanceof Error ? err.message : 'Failed to load analysis result')
      setLoading(false)
    }
  }

  const handleExport = async (format: 'pdf' | 'docx' | 'json') => {
    try {
      // Show loading state
      setLoading(true)
      
      // Trigger backend export
      let response
      if (format === 'json') {
        // JSON export (existing implementation)
        const dataStr = JSON.stringify(analysis, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        const url = URL.createObjectURL(dataBlob)
        const link = document.createElement('a')
        link.href = url
        link.download = `contract-analysis-${taskId}.json`
        link.click()
        URL.revokeObjectURL(url)
        
        toast({
          title: 'Export Successful',
          description: `Report exported as JSON`
        })
      } else {
        // PDF or DOCX export (NEW - real implementation)
        const includeCharts = format !== 'json'
        
        response = await apiClient.exportReportPDF(taskId, includeCharts)
        
        if (response.success && response.data && response.data.download_url) {
          // Download file
          window.open(response.data.download_url, '_blank')
          
          toast({
            title: 'Export Successful',
            description: `${format.toUpperCase()} export completed`
          })
        } else {
          toast({
            title: 'Export Failed',
            description: response.data?.message || 'Unknown export error',
            variant: 'destructive'
          })
        }
      }
      
    } catch (err) {
      console.error('Export failed:', err)
      toast({
        title: 'Export Failed',
        description: err instanceof Error ? err.message : 'Failed to export report',
        duration: 5000,
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  const getRiskBadge = (severity: string) => {
    switch (severity) {
      case 'high':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="h-3 w-3 mr-1" />
            High Risk
          </span>
        )
      case 'medium':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Medium Risk
          </span>
        )
      case 'low':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Low Risk
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {severity}
          </span>
        )
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <Toaster />
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center min-h-96">
            <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <Toaster />
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
            <XCircle className="h-16 w-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Error Loading Report
            </h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => router.push('/contracts')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Back to Contracts
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!analysis) {
    return null
  }

  const report = analysis.report || {}
  const findings = report.findings || []
  const riskMatrix = report.risk_matrix || {}

  return (
    <div className="p-8">
      <Toaster />

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <button
              onClick={() => router.push('/contracts')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Contracts
            </button>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Contract Analysis Report
            </h1>
            <p className="text-gray-600">
              Task ID: {taskId} • Contract Type: {analysis.contract_type}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleExport('pdf')}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <Download className="h-4 w-4" />
              PDF
            </button>
            <button
              onClick={() => handleExport('docx')}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <Download className="h-4 w-4" />
              DOCX
            </button>
            <button
              onClick={() => handleExport('json')}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <Download className="h-4 w-4" />
              JSON
            </button>
            <button
              onClick={() => window.print()}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <Printer className="h-4 w-4" />
              Print
            </button>
          </div>
        </div>

        {/* Overall Risk Badge */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-1">Overall Risk Assessment</h2>
              <p className="text-sm text-gray-600">
                Based on analysis of {analysis.agent_history?.length || 0} agents
              </p>
            </div>
            <div className="text-right">
              <div className="mb-2">{getRiskBadge(analysis.overall_risk)}</div>
              <div className="text-sm text-gray-600">
                Confidence: {(analysis.validation_confidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>

        {/* Risk Matrix */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Matrix</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">Legal Risk</h3>
              <p className="text-2xl font-bold text-gray-900">{riskMatrix.legal_risk || 'N/A'}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">Financial Risk</h3>
              <p className="text-2xl font-bold text-gray-900">{riskMatrix.financial_risk || 'N/A'}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">Operational Risk</h3>
              <p className="text-2xl font-bold text-gray-900">{riskMatrix.operational_risk || 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('summary')}
              className={`flex-1 px-6 py-4 font-medium transition-colors ${
                activeTab === 'summary'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Executive Summary
            </button>
            <button
              onClick={() => setActiveTab('findings')}
              className={`flex-1 px-6 py-4 font-medium transition-colors ${
                activeTab === 'findings'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Findings ({findings.length})
            </button>
            <button
              onClick={() => setActiveTab('suggestions')}
              className={`flex-1 px-6 py-4 font-medium transition-colors ${
                activeTab === 'suggestions'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Suggestions ({report.suggestions?.length || 0})
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'summary' && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">Executive Summary</h3>
                <p className="text-gray-700 leading-relaxed">
                  {report.executive_summary || analysis.final_answer || 'No summary available'}
                </p>

                <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">Analysis Confidence</div>
                    <div className="text-xl font-bold text-gray-900">
                      {(analysis.analysis_confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">Validation Confidence</div>
                    <div className="text-xl font-bold text-gray-900">
                      {(analysis.validation_confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">Issues Found</div>
                    <div className="text-xl font-bold text-gray-900">{findings.length}</div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">Agents Executed</div>
                    <div className="text-xl font-bold text-gray-900">
                      {analysis.agent_history?.length || 0}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'findings' && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">Findings</h3>
                {findings.length === 0 ? (
                  <div className="text-center py-12 text-gray-600">
                    <CheckCircle2 className="h-16 w-16 text-green-600 mx-auto mb-4" />
                    <p>No issues found. This contract appears to be compliant.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {findings.map((finding: any, index: number) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            {getRiskBadge(finding.severity)}
                            <span className="font-medium text-gray-900">{finding.category}</span>
                          </div>
                        </div>
                        <p className="text-gray-700 mb-3">{finding.description}</p>
                        {finding.suggestion && (
                          <div className="bg-blue-50 rounded-lg p-3">
                            <p className="text-sm text-blue-900">
                              <strong>Suggestion:</strong> {finding.suggestion}
                            </p>
                          </div>
                        )}
                        {finding.citation && (
                          <div className="mt-2 text-sm text-gray-600">
                            <FileText className="inline h-3 w-3 mr-1" />
                            Reference: {finding.citation}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'suggestions' && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">Suggestions</h3>
                {report.suggestions && report.suggestions.length > 0 ? (
                  <div className="space-y-3">
                    {report.suggestions.map((suggestion: string, index: number) => (
                      <div key={index} className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
                        <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                        <p className="text-gray-700">{suggestion}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-600">
                    <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p>No specific suggestions available.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
