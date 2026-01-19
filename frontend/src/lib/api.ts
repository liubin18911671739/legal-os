import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiResponse<T> {
  success: boolean
  message?: string
  data?: T
}

export interface ApiError {
  success: false
  message: string
  detail?: string
}

export interface Document {
  id: string
  title: string
  file_name: string
  file_type: 'pdf' | 'docx' | 'txt'
  status: 'uploading' | 'processing' | 'indexed' | 'failed'
  vectorized: boolean
  created_at: string
  updated_at: string
  meta?: Record<string, any>
  file_path?: string
  file_size?: string
}

export interface DocumentListResponse {
  items: Document[]
  total: number
  page: number
  size: number
  pages: number
}

export interface Task {
  id: string
  task_type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_stage?: string
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface ContractAnalysisRequest {
  contract_id: string
  contract_text: string
  contract_type: 'employment' | 'sales' | 'lease' | 'service' | 'purchase' | 'other'
  user_query?: string
}

export interface ContractAnalysisResponse {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  message: string
}

export interface AnalysisResult {
  task_id: string
  contract_id: string
  contract_type: string
  task_status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  agent_history: string[]
  analysis_confidence: number
  overall_risk: 'low' | 'medium' | 'high' | 'unknown'
  validation_confidence: number
  final_answer: string
  report?: {
    executive_summary: string
    findings: Array<{
      category: string
      severity: 'low' | 'medium' | 'high'
      description: string
      suggestion?: string
      citation?: string
    }>
    risk_matrix: {
      legal_risk: string
      financial_risk: string
      operational_rost: string
    }
    suggestions: string[]
  }
}

export interface ExportRequest {
  task_id: string
  format: 'pdf' | 'docx' | 'json'
  include_charts?: boolean
}

export interface ExportResponse {
  export_id: string
  status: string
  message: string
  download_url?: string
}

export interface ExportStatus {
  export_id: string
  status: string
  message: string
  download_url?: string
  file_size?: number
  error?: string
}

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiResponse<T> {
  success: boolean
  message?: string
  data?: T
}

export interface ApiError {
  success: false
  message: string
  detail?: string
}

export interface Document {
  id: string
  title: string
  file_name: string
  file_type: 'pdf' | 'docx' | 'txt'
  status: 'uploading' | 'processing' | 'indexed' | 'failed'
  vectorized: boolean
  created_at: string
  updated_at: string
  meta?: Record<string, any>
  file_path?: string
  file_size?: string
}

export interface DocumentListResponse {
  items: Document[]
  total: number
  page: number
  size: number
  pages: number
}

export interface Task {
  id: string
  task_type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_stage?: string
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface ContractAnalysisRequest {
  contract_id: string
  contract_text: string
  contract_type: 'employment' | 'sales' | 'lease' | 'service' | 'purchase' | 'other'
  user_query?: string
}

export interface ContractAnalysisResponse {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  message: string
}

export interface AnalysisResult {
  task_id: string
  contract_id: string
  contract_type: string
  task_status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  agent_history: string[]
  analysis_confidence: number
  overall_risk: 'low' | 'medium' | 'high' | 'unknown'
  validation_confidence: number
  final_answer: string
  report?: {
    executive_summary: string
    findings: Array<{
      category: string
      severity: 'low' | 'medium' | 'high'
      description: string
      suggestion?: string
      citation?: string
    }>
    risk_matrix: {
      legal_risk: string
      financial_risk: string
      operational_risk: string
    }
    suggestions: string[]
  }
}

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const error: ApiError = await response.json()
        throw new Error(error.message || 'API request failed')
      }

      return await response.json()
    } catch (error) {
      console.error('API request error:', error)
      throw error
    }
  }

  // Documents API
  async getDocuments(page: number = 1, size: number = 20): Promise<DocumentListResponse> {
    return this.request<DocumentListResponse>(`/api/v1/documents/?page=${page}&size=${size}`)
  }

  async getDocument(id: string): Promise<Document> {
    return this.request<Document>(`/api/v1/documents/${id}`)
  }

  async createDocument(data: Partial<Document>): Promise<Document> {
    return this.request<Document>('/api/v1/documents/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateDocument(id: string, data: Partial<Document>): Promise<Document> {
    return this.request<Document>(`/api/v1/documents/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteDocument(id: string): Promise<void> {
    return this.request<void>(`/api/v1/documents/${id}`, {
      method: 'DELETE',
    })
  }

  // Tasks API
  async getTasks(page: number = 1, size: number = 20): Promise<Task[]> {
    return this.request<Task[]>(`/api/v1/tasks/?page=${page}&size=${size}`)
  }

  async getTask(id: string): Promise<Task> {
    return this.request<Task>(`/api/v1/tasks/${id}`)
  }

  async createTask(data: Partial<Task>): Promise<Task> {
    return this.request<Task>('/api/v1/tasks/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateTask(id: string, data: Partial<Task>): Promise<Task> {
    return this.request<Task>(`/api/v1/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  // Contract Analysis API
  async analyzeContract(request: ContractAnalysisRequest): Promise<ContractAnalysisResponse> {
    return this.request<ContractAnalysisResponse>('/api/v1/contracts/analyze', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getContractAnalysis(taskId: string): Promise<AnalysisResult> {
    return this.request<AnalysisResult>(`/api/v1/contracts/analysis/${taskId}`)
  }

  async getContractTaskStatus(taskId: string): Promise<Task> {
    return this.request<Task>(`/api/v1/contracts/tasks/${taskId}`)
  }

  async exportReportPDF(taskId: string, includeCharts: boolean = false): Promise<Blob> {
    const response = await this.request<ApiResponse<Blob>>(`/export/pdf`, {
      method: 'POST',
      body: JSON.stringify({
        task_id: taskId,
        include_charts: includeCharts,
      }),
    })

    if (response.success && response.data) {
      return response.data as Blob
    } else {
      throw new Error(response.message || 'PDF export failed')
    }
  }

  async exportReportDOCX(taskId: string, includeCharts: boolean = false): Promise<Blob> {
    const response = await this.request<ApiResponse<Blob>>(`/export/docx`, {
      method: 'POST',
      body: JSON.stringify({
        task_id: taskId,
        include_charts: includeCharts,
      }),
    })

    if (response.success && response.data) {
      return response.data as Blob
    } else {
      throw new Error(response.message || 'DOCX export failed')
    }
  }

  async getExportStatus(taskId: string): Promise<ExportStatus> {
    return this.request<ExportStatus>(`/export/status/${taskId}`)
  }
}

export const apiClient = new ApiClient()
