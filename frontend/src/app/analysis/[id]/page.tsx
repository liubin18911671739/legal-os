'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Toaster } from '@/components/toaster'
import { useToast } from '@/hooks/use-toast'
import { Loader2, CheckCircle2, AlertCircle, XCircle, Clock, Activity } from 'lucide-react'

interface ProgressState {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_stage?: string
  agent_history?: string[]
  error_message?: string
}

const agentNames: Record<string, string> = {
  'coordinator': 'Coordinator Agent',
  'retrieval': 'Retrieval Agent',
  'analysis': 'Analysis Agent',
  'review': 'Review Agent',
  'validation': 'Validation Agent',
  'report': 'Report Agent',
}

const stageDescriptions: Record<string, string> = {
  'pending': 'Task queued, waiting to start...',
  'coordinator': 'Analyzing contract structure and type...',
  'retrieval': 'Searching knowledge base for relevant clauses...',
  'analysis': 'Extracting entities and classifying clauses...',
  'review': 'Checking compliance and assessing risks...',
  'validation': 'Validating analysis consistency...',
  'report': 'Generating final report...',
  'completed': 'Analysis completed successfully!',
  'failed': 'Analysis failed. Please try again.',
  'cancelled': 'Analysis was cancelled.',
}

export default function AnalysisProgressPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const [progress, setProgress] = useState<ProgressState | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const taskId = params.id as string

  useEffect(() => {
    if (!taskId) {
      setError('Task ID is required')
      setLoading(false)
      return
    }

    // Try WebSocket first
    let ws: WebSocket | null = null
    try {
      ws = apiClient.connectTaskWebSocket(taskId)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setLoading(false)
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === 'task_update') {
          setProgress({
            task_id: data.task_id,
            status: data.status,
            progress: data.progress,
            current_stage: data.current_stage,
            agent_history: data.agent_history,
            error_message: data.error_message,
          })
        } else if (data.type === 'task_complete') {
          toast({
            title: 'Analysis Completed',
            description: 'Contract analysis has been completed successfully',
          })
          // Navigate to report page after delay
          setTimeout(() => {
            router.push(`/report/${taskId}`)
          }, 2000)
        } else if (data.type === 'error') {
          setError(data.message)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        // Fallback to polling
        console.log('Falling back to polling...')
        fetchTaskStatus()
        pollIntervalRef.current = setInterval(fetchTaskStatus, 2000)
      }

      ws.onclose = () => {
        console.log('WebSocket closed')
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current)
        }
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      // Fallback to polling
      fetchTaskStatus()
      pollIntervalRef.current = setInterval(fetchTaskStatus, 2000)
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [taskId])

  const fetchTaskStatus = async () => {
    try {
      const task = await apiClient.getContractTaskStatus(taskId)
      setProgress({
        task_id: task.id,
        status: task.status as any,
        progress: task.progress || 0,
        current_stage: task.current_stage,
        agent_history: task.input_data?.agent_history || [],
        error_message: task.error_message,
      })
      setLoading(false)
      setError(null)

      // Stop polling if task is complete or failed
      if (task.status === 'completed' || task.status === 'failed') {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
        }

        if (task.status === 'completed') {
          toast({
            title: 'Analysis Completed',
            description: 'Contract analysis has been completed successfully',
          })
          // Navigate to report page after delay
          setTimeout(() => {
            router.push(`/report/${taskId}`)
          }, 2000)
        }
      }
    } catch (err) {
      console.error('Failed to fetch task status:', err)
      if (!error) {
        setError(err instanceof Error ? err.message : 'Failed to load task status')
        setLoading(false)
      }
    }
  }

  const handleCancel = async () => {
    try {
      await apiClient.updateTask(taskId, { status: 'cancelled' })
      toast({
        title: 'Analysis Cancelled',
        description: 'The analysis has been cancelled',
      })
      router.push('/contracts')
    } catch (err) {
      toast({
        title: 'Cancellation Failed',
        description: err instanceof Error ? err.message : 'Failed to cancel analysis',
        duration: 5000,
      })
    }
  }

  const handleRetry = () => {
    router.push('/upload')
  }

  const handleViewReport = () => {
    router.push(`/report/${taskId}`)
  }

  if (loading) {
    return (
      <div className="p-8">
        <Toaster />
        <div className="max-w-4xl mx-auto">
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
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
            <AlertCircle className="h-16 w-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Error Loading Task
            </h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={handleRetry}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!progress) {
    return null
  }

  const getStatusIcon = () => {
    switch (progress.status) {
      case 'pending':
        return <Clock className="h-12 w-12 text-gray-500" />
      case 'running':
        return <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      case 'completed':
        return <CheckCircle2 className="h-12 w-12 text-green-600" />
      case 'failed':
        return <XCircle className="h-12 w-12 text-red-600" />
      case 'cancelled':
        return <XCircle className="h-12 w-12 text-gray-600" />
    }
  }

  const getStatusText = () => {
    switch (progress.status) {
      case 'pending':
        return 'Waiting to Start'
      case 'running':
        return 'Processing...'
      case 'completed':
        return 'Completed'
      case 'failed':
        return 'Failed'
      case 'cancelled':
        return 'Cancelled'
    }
  }

  const getCurrentStage = () => {
    if (progress.status === 'completed') return 'completed'
    if (progress.status === 'failed' || progress.status === 'cancelled') return progress.status
    return progress.current_stage || 'pending'
  }

  const currentStage = getCurrentStage()
  const stageDescription = stageDescriptions[currentStage] || 'Processing...'

  return (
    <div className="p-8">
      <Toaster />

      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Contract Analysis Progress</h1>
        <p className="text-gray-600 mb-8">
          Task ID: {taskId}
        </p>

        {/* Status Card */}
        <div className="bg-white rounded-xl border border-gray-200 p-8 mb-8">
          <div className="flex items-center gap-6">
            {getStatusIcon()}
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-2xl font-bold text-gray-900">
                  {getStatusText()}
                </h2>
                <span className="text-3xl font-bold text-blue-600">
                  {progress.progress}%
                </span>
              </div>
              <p className="text-gray-600">
                {stageDescription}
              </p>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-6">
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progress.progress}%` }}
              />
            </div>
          </div>

          {/* Error Message */}
          {progress.error_message && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{progress.error_message}</p>
            </div>
          )}
        </div>

        {/* Agent History */}
        {progress.agent_history && progress.agent_history.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-8 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="h-6 w-6" />
              Agent Execution History
            </h3>
            <div className="space-y-3">
              {progress.agent_history.map((agent, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${
                    index === progress.agent_history!.length - 1 && progress.status === 'running'
                      ? 'bg-blue-50 border-blue-300'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {index === progress.agent_history!.length - 1 && progress.status === 'running' ? (
                      <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                    )}
                    <span className="font-medium text-gray-900">
                      {agentNames[agent] || agent}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4">
          {progress.status === 'running' && (
            <button
              onClick={handleCancel}
              className="flex-1 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Cancel Analysis
            </button>
          )}

          {progress.status === 'completed' && (
            <button
              onClick={handleViewReport}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              View Full Report
            </button>
          )}

          {(progress.status === 'failed' || progress.status === 'cancelled') && (
            <button
              onClick={handleRetry}
              className="flex-1 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Upload New Contract
            </button>
          )}

          <button
            onClick={() => router.push('/contracts')}
            className="px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Back to Contracts
          </button>
        </div>
      </div>
    </div>
  )
}
