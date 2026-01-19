'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Scale, FileText, BarChart3, UploadCloud, Activity, TrendingUp } from 'lucide-react'

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: BarChart3,
  },
  {
    name: 'Upload Contract',
    href: '/upload',
    icon: UploadCloud,
  },
  {
    name: 'Contracts',
    href: '/contracts',
    icon: FileText,
  },
  {
    name: 'Knowledge Base',
    href: '/knowledge',
    icon: Scale,
  },
  {
    name: 'Analysis Progress',
    href: '/analysis',
    icon: Activity,
  },
  {
    name: 'Evaluation',
    href: '/evaluation',
    icon: TrendingUp,
  },
]

export function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-200 bg-gray-50/50">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-900">
            LegalOS
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Legal Intelligence Analysis
          </p>
        </div>

        <nav className="mt-6 px-3">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors mb-1',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-200'
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
