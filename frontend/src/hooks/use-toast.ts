'use client'

import { useState, useCallback, useEffect } from 'react'

export interface Toast {
  id: string
  title?: string
  description?: string
  action?: React.ReactNode
  duration?: number
}

let toastCount = 0

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const toast = useCallback(
    ({ title, description, action, duration = 5000 }: Omit<Toast, 'id'>) => {
      const id = `toast-${toastCount++}`
      const newToast: Toast = {
        id,
        title,
        description,
        action,
        duration,
      }

      setToasts((current) => [...current, newToast])

      if (duration > 0) {
        setTimeout(() => {
          setToasts((current) => current.filter((t) => t.id !== id))
        }, duration)
      }

      return id
    },
    [setToasts]
  )

  const dismiss = useCallback((toastId: string) => {
    setToasts((current) => current.filter((t) => t.id !== toastId))
  }, [])

  return {
    toasts,
    toast,
    dismiss,
  }
}
