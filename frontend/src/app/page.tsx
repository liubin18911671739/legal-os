'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { zhCN } from '@/lib/translations'
import { UploadCloud, FileText, Scale, ArrowRight, FileCheck, Brain, FileText as FileTextIcon } from 'lucide-react'

export default function Home() {
  const features = [
    {
      title: zhCN.home.features.upload.title,
      description: zhCN.home.features.upload.description,
      icon: UploadCloud,
      color: 'bg-blue-100 text-blue-600',
      href: '/upload',
    },
    {
      title: zhCN.home.features.analyze.title,
      description: zhCN.home.features.analyze.description,
      icon: Brain,
      color: 'bg-purple-100 text-purple-600',
      href: '/contracts',
    },
    {
      title: zhCN.home.features.report.title,
      description: zhCN.home.features.report.description,
      icon: FileTextIcon,
      color: 'bg-green-100 text-green-600',
      href: '/analysis',
    },
  ]

  const steps = [
    {
      number: '1',
      title: zhCN.home.features.upload.title,
      description: '拖拽或选择您的合同文件',
      icon: UploadCloud,
    },
    {
      number: '2',
      title: zhCN.home.features.analyze.title,
      description: '多智能体 RAG 系统分析合同',
      icon: Brain,
    },
    {
      number: '3',
      title: zhCN.home.features.report.title,
      description: '获取详细的合规和风险评估',
      icon: FileCheck,
    },
  ]

  return (
    <div className="space-y-12">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          {zhCN.home.welcome}
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl">
          {zhCN.home.description}
        </p>
        <div className="flex gap-4 pt-2">
          <Link href="/upload">
            <Button size="lg" className="gap-2">
              {zhCN.home.getStarted}
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
          <Link href="/contracts">
            <Button size="lg" variant="outline">
              {zhCN.contracts.title}
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon
          return (
            <Link key={feature.title} href={feature.href}>
              <Card className="h-full transition-all duration-200 hover:shadow-lg hover:border-blue-300 cursor-pointer group">
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">
                    {feature.title}
                  </CardTitle>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>
          )
        })}
      </div>

      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-2xl">
            使用流程
          </CardTitle>
          <CardDescription className="text-base text-gray-700">
            三步完成合同智能分析
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, index) => {
              const Icon = step.icon
              return (
                <div key={step.number} className="relative">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                      {step.number}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Icon className="h-5 w-5 text-blue-600" />
                        <h3 className="font-semibold text-gray-900">
                          {step.title}
                        </h3>
                      </div>
                      <p className="text-gray-600 text-sm">
                        {step.description}
                      </p>
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <div className="hidden md:block absolute top-5 -right-4 w-8 h-0.5 bg-blue-300" />
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
