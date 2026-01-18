'use client'

export default function AnalysisPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Analysis Progress</h1>
      <p className="text-gray-600 mb-8">
        Select a contract to analyze or view current progress
      </p>

      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <p className="text-gray-600 mb-4">
          Please upload a contract first or select from contracts page
        </p>
        <a
          href="/upload"
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Go to Upload
        </a>
      </div>
    </div>
  )
}
