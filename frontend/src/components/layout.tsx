'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { zhCN } from '@/lib/translations'
import { Scale, FileText, BarChart3, UploadCloud, Activity, TrendingUp, LayoutDashboard } from 'lucide-react'

const navigation = [
  {
    name: zhCN.nav.dashboard,
    href: '/',
    icon: LayoutDashboard,
  },
  {
    name: zhCN.nav.upload,
    href: '/upload',
    icon: UploadCloud,
  },
  {
    name: zhCN.nav.contracts,
    href: '/contracts',
    icon: FileText,
  },
  {
    name: zhCN.nav.knowledge,
    href: '/knowledge',
    icon: Scale,
  },
  {
    name: zhCN.nav.analysis,
    href: '/analysis',
    icon: Activity,
  },
  {
    name: zhCN.nav.evaluation,
    href: '/evaluation',
    icon: TrendingUp,
  },
]

export function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen flex bg-gray-50">
      <aside className="w-64 border-r border-gray-200 bg-white shadow-sm flex flex-col">
        <div className="p-6 border-b border-gray-100">
          <h1 className="text-2xl font-bold text-gray-900">
            LegalOS
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {zhCN.home.subtitle}
          </p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                <span className="truncate">{item.name}</span>
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <div className="text-xs text-gray-400">
            © 2024 LegalOS
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
