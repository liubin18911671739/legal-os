'use client'

export default function ReportPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Analysis Report</h1>
      <p className="text-gray-600 mb-8">
        Select a contract to view its analysis report
      </p>

      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <p className="text-gray-600 mb-4">
          No report selected. Please analyze a contract first.
        </p>
        <a
          href="/contracts"
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          View Contracts
        </a>
      </div>
    </div>
  )
}
