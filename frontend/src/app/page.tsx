export default function Home() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">
        Welcome to LegalOS
      </h1>
      <p className="text-gray-600 text-lg mb-8">
        Enterprise Legal Intelligence Analysis System
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <a
          href="/upload"
          className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-blue-500 transition-all group"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200">
              <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003-3h6a3 3 0 003-3v1M4 8a3 3 0 003-3 0V3m0 2v3a3 3 0 016-3h6a3 3 0 013 3V6a3 3 0 01-3 0v6z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              Upload Contract
            </h3>
          </div>
          <p className="text-gray-600">
            Upload PDF, DOCX, or TXT files for AI-powered analysis
          </p>
        </a>

        <a
          href="/contracts"
          className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-blue-500 transition-all group"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-green-100 rounded-lg group-hover:bg-green-200">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7m2 5H5a2 2 0 00-2-2V5a2 2 0 00-2-2v9m0 0v6h.01v-6H5m-2 2V5a2 2 0 00-2-2H4z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              View Contracts
            </h3>
          </div>
          <p className="text-gray-600">
            Browse and manage all uploaded contracts
          </p>
        </a>

        <a
          href="/knowledge"
          className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-blue-500 transition-all group"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-purple-100 rounded-lg group-hover:bg-purple-200">
              <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7 5H4a2 2 0 00-2-2v4a2 2 0 012-2 2v6a2 2 0 012-2 2v-6a2 2 0 00-2-2H4z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              Knowledge Base
            </h3>
          </div>
          <p className="text-gray-600">
            Manage legal documents and templates
          </p>
        </a>
      </div>

      <div className="mt-12 bg-blue-50 rounded-xl border border-blue-200 p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          How It Works
        </h2>
        <div className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
              1
            </div>
            <p className="text-gray-700">
              <strong className="text-gray-900">Upload Contract</strong> - Drag & drop or select your contract file
            </p>
          </div>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
              2
            </div>
            <p className="text-gray-700">
              <strong className="text-gray-900">AI Analysis</strong> - Multi-agent RAG system analyzes your contract
            </p>
          </div>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
              3
            </div>
            <p className="text-gray-700">
              <strong className="text-gray-900">Review Report</strong> - Get detailed compliance and risk assessment
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
