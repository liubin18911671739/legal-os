'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'
import { BarChart3, TrendingUp, Clock, DollarSign, CheckCircle2, AlertTriangle, PlayCircle, Download, RefreshCw } from 'lucide-react'

interface EvaluationResult {
  baseline_type: string
  duration: number
  token_usage: number
  cost: number
  metrics: {
    precision: number
    recall: number
    f1_score: number
    hallucination_rate: number
  }
  error?: string
}

interface EvaluationComparison {
  [baseline: string]: {
    f1_score: number
    hallucination_rate: number
    duration: number
    precision: number
    recall: number
    token_usage: number
    cost: number
  }
}

interface EvaluationResults {
  evaluation_id: string
  contract_id: string
  results: EvaluationResult[]
  comparison: EvaluationComparison
  timestamp: string
}

interface DatasetContract {
  id: string
  title: string
  contract_type: string
  overall_risk: string
  compliance_status: string
  risk_points_count: number
}

interface DatasetInfo {
  name: string
  version: string
  total_contracts: number
  total_risk_points: number
  contract_type_distribution: Record<string, number>
  severity_distribution: Record<string, number>
}

export default function EvaluationPage() {
  const { toast } = useToast()
  const [datasetInfo, setDatasetInfo] = useState<DatasetInfo | null>(null)
  const [contracts, setContracts] = useState<DatasetContract[]>([])
  const [selectedContract, setSelectedContract] = useState<string | null>(null)
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResults | null>(null)
  const [loading, setLoading] = useState(true)
  const [runningEvaluation, setRunningEvaluation] = useState(false)

  useEffect(() => {
    loadDatasetInfo()
    loadContracts()
  }, [])

  const loadDatasetInfo = async () => {
    try {
      const info = await apiClient.getEvaluationDatasetInfo()
      setDatasetInfo(info)
    } catch (error) {
      toast({
        title: 'Failed to load dataset info',
        description: error instanceof Error ? error.message : 'An error occurred',
        duration: 5000,
      })
    } finally {
      setLoading(false)
    }
  }

  const loadContracts = async () => {
    try {
      const contracts = await apiClient.getEvaluationContracts()
      setContracts(contracts)
    } catch (error) {
      console.error('Failed to load contracts:', error)
    }
  }

  const runEvaluation = async (contractId: string) => {
    if (!contractId) return

    setRunningEvaluation(true)
    setSelectedContract(contractId)

    try {
      const response = await apiClient.runEvaluation({
        contract_id: contractId,
        baseline_types: ['no_rag', 'simple_rag', 'multi_agent_rag'],
        model_name: 'glm-4',
        temperature: 0.7,
        max_tokens: 2000,
      })

      toast({
        title: 'Evaluation Started',
        description: `Evaluation ${response.evaluation_id} has been started`,
      })

      // Poll for results
      pollEvaluationResults(response.evaluation_id)
    } catch (error) {
      toast({
        title: 'Evaluation Failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        duration: 5000,
      })
    } finally {
      setRunningEvaluation(false)
    }
  }

  const pollEvaluationResults = async (evaluationId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const results = await apiClient.getEvaluationResults(evaluationId)
        setEvaluationResults(results)

        // Stop polling if we have results
        if (results.results.length > 0) {
          clearInterval(pollInterval)
          toast({
            title: 'Evaluation Completed',
            description: 'All baseline experiments have completed',
          })
        }
      } catch (error) {
        console.error('Failed to fetch results:', error)
        clearInterval(pollInterval)
      }
    }, 2000)

    // Stop after 60 seconds
    setTimeout(() => {
      clearInterval(pollInterval)
    }, 60000)
  }

  const handleCreateSampleDataset = async () => {
    try {
      const response = await apiClient.createSampleDataset()
      toast({
        title: 'Sample Dataset Created',
        description: `${response.contracts_count} sample contracts have been created`,
      })
      loadDatasetInfo()
      loadContracts()
    } catch (error) {
      toast({
        title: 'Failed to Create Sample Dataset',
        description: error instanceof Error ? error.message : 'An error occurred',
        duration: 5000,
      })
    }
  }

  const handleExportResults = () => {
    if (!evaluationResults) return

    const dataStr = JSON.stringify(evaluationResults, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `evaluation-${evaluationResults.evaluation_id}.json`
    link.click()
    URL.revokeObjectURL(url)

    toast({
      title: 'Results Exported',
      description: 'Evaluation results have been downloaded',
    })
  }

  if (loading) {
    return (
      <div className="p-8">
        <Toaster />
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center min-h-96">
            <RefreshCw className="h-12 w-12 animate-spin text-blue-600" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <Toaster />

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Evaluation Dashboard</h1>
            <p className="text-gray-600">
              Compare baseline experiments and evaluate model performance
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCreateSampleDataset}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="h-4 w-4" />
              Create Sample Dataset
            </button>
          </div>
        </div>

        {/* Dataset Info Cards */}
        {datasetInfo && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="h-5 w-5 text-blue-600" />
                <span className="text-sm text-gray-600">Total Contracts</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{datasetInfo.total_contracts}</p>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <span className="text-sm text-gray-600">Risk Points</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{datasetInfo.total_risk_points}</p>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <span className="text-sm text-gray-600">Dataset Version</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{datasetInfo.version}</p>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <span className="text-sm text-gray-600">Risk Distribution</span>
              </div>
              <p className="text-sm text-gray-600">
                High: {datasetInfo.severity_distribution.high || 0} | 
                Medium: {datasetInfo.severity_distribution.medium || 0} | 
                Low: {datasetInfo.severity_distribution.low || 0}
              </p>
            </div>
          </div>
        )}

        {/* Contract Selection */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Select Contract to Evaluate</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {contracts.map((contract) => (
              <div
                key={contract.id}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                  selectedContract === contract.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedContract(contract.id)}
              >
                <h3 className="font-medium text-gray-900 mb-2">{contract.title}</h3>
                <div className="space-y-1 text-sm">
                  <p><strong>Type:</strong> {contract.contract_type}</p>
                  <p><strong>Risk:</strong> {contract.overall_risk}</p>
                  <p><strong>Status:</strong> {contract.compliance_status}</p>
                  <p><strong>Risk Points:</strong> {contract.risk_points_count}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex gap-2">
            <button
              onClick={() => runEvaluation(selectedContract || '')}
              disabled={!selectedContract || runningEvaluation}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {runningEvaluation ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Running Evaluation...
                </>
              ) : (
                <>
                  <PlayCircle className="h-4 w-4" />
                  Run Evaluation
                </>
              )}
            </button>

            {evaluationResults && (
              <button
                onClick={handleExportResults}
                className="flex items-center gap-2 px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                <Download className="h-4 w-4" />
                Export Results
              </button>
            )}
          </div>
        </div>

        {/* Evaluation Results */}
        {evaluationResults && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Evaluation Results</h2>
              <span className="text-sm text-gray-600">ID: {evaluationResults.evaluation_id}</span>
            </div>

            {/* Metrics Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Baseline</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Precision</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Recall</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">F1 Score</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Hallucination Rate</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Duration (s)</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Tokens</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Cost ($)</th>
                  </tr>
                </thead>
                <tbody>
                  {evaluationResults.results.map((result, index) => (
                    <tr key={index} className="border-b border-gray-100">
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          result.baseline_type === 'multi_agent_rag' ? 'bg-green-100 text-green-800' :
                          result.baseline_type === 'simple_rag' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {result.baseline_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="text-right py-3 px-4">{(result.metrics.precision * 100).toFixed(1)}%</td>
                      <td className="text-right py-3 px-4">{(result.metrics.recall * 100).toFixed(1)}%</td>
                      <td className="text-right py-3 px-4">
                        <span className={`font-bold ${
                          result.metrics.f1_score > 0.8 ? 'text-green-600' :
                          result.metrics.f1_score > 0.7 ? 'text-blue-600' :
                          'text-gray-600'
                        }`}>
                          {(result.metrics.f1_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="text-right py-3 px-4">{(result.metrics.hallucination_rate * 100).toFixed(1)}%</td>
                      <td className="text-right py-3 px-4">{result.duration.toFixed(1)}s</td>
                      <td className="text-right py-3 px-4">{result.token_usage}</td>
                      <td className="text-right py-3 px-4">${result.cost.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Comparison Chart */}
            <div className="mt-8">
              <h3 className="text-lg font-bold text-gray-900 mb-4">F1 Score Comparison</h3>
              <div className="space-y-4">
                {evaluationResults.results.map((result) => {
                  const percentage = result.metrics.f1_score * 100
                  const color = result.baseline_type === 'multi_agent_rag' ? 'bg-green-600' :
                              result.baseline_type === 'simple_rag' ? 'bg-blue-600' :
                              'bg-gray-400'
                  return (
                    <div key={result.baseline_type}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          {result.baseline_type.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-600">{percentage.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`${color} h-3 rounded-full transition-all duration-500`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Performance Summary */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="h-5 w-5 text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">Avg Duration</span>
                </div>
                <p className="text-xl font-bold text-gray-900">
                  {evaluationResults.results.length > 0
                    ? (evaluationResults.results.reduce((acc, r) => acc + r.duration, 0) / evaluationResults.results.length).toFixed(1) + 's'
                    : 'N/A'}
                </p>
              </div>

              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium text-gray-900">Avg Cost</span>
                </div>
                <p className="text-xl font-bold text-gray-900">
                  {evaluationResults.results.length > 0
                    ? '$' + (evaluationResults.results.reduce((acc, r) => acc + r.cost, 0) / evaluationResults.results.length).toFixed(3)
                    : 'N/A'}
                </p>
              </div>

              <div className="bg-purple-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-5 w-5 text-purple-600" />
                  <span className="text-sm font-medium text-gray-900">Best F1 Score</span>
                </div>
                <p className="text-xl font-bold text-gray-900">
                  {evaluationResults.results.length > 0
                    ? (Math.max(...evaluationResults.results.map(r => r.metrics.f1_score)) * 100).toFixed(1) + '%'
                    : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!evaluationResults && contracts.length === 0 && (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <AlertTriangle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No contracts available
            </h3>
            <p className="text-gray-600 mb-4">
              Create a sample dataset to get started with evaluation
            </p>
            <button
              onClick={handleCreateSampleDataset}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Sample Dataset
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
