'use client'

import { useToast } from '@/hooks/use-toast'

export function Toaster() {
  const { toasts } = useToast()

  return (
    <div className="fixed bottom-0 right-0 z-[100] flex flex-col gap-2 p-4">
      {toasts.map(function ({ id, title, description, action, ...props }) {
        return (
          <div
            key={id}
            {...props}
            className="group relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-4 pr-8 shadow-lg transition-all"
          >
            <div className="grid gap-1">
              {title && <div className="text-sm font-semibold">{title}</div>}
              {description && (
                <div className="text-sm opacity-90">{description}</div>
              )}
            </div>
            {action}
            <button
              onClick={() => {
                // Toast dismiss action will be handled by the hook
                const toast = document.getElementById(`toast-${id}`)
                if (toast) {
                  toast.style.opacity = '0'
                  setTimeout(() => {
                    toast.remove()
                  }, 300)
                }
              }}
              className="absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100"
            >
              ×
            </button>
          </div>
        )
      })}
    </div>
  )
}
