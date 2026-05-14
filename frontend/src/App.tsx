import { useState, useEffect } from 'react'
import apiClient from './api/client'
import type { Claim } from './types/claim'

function App() {
  // --- UI States ---
  const [status, setStatus] = useState<string>('Checking...')
  const [claims, setClaims] = useState<Claim[]>([])
  const [loading, setLoading] = useState(true)
  
  // --- Form State ---
  const [formData, setFormData] = useState({
    policy_number: '',
    claim_amount: 0,
    description: ''
  })

  // --- File States ---
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  // --- 1. Fetch All Claims (GET) ---
  const fetchClaims = async () => {
    try {
      const response = await apiClient.get('/claims/')
      setClaims(response.data)
    } catch (err) {
      console.error("Fetch error:", err)
    }
  }

  // --- 2. Initial Connection Check ---
  useEffect(() => {
    apiClient.get('/')
      .then(() => {
        setStatus('Backend: Connected')
        fetchClaims()
      })
      .catch(() => setStatus('Backend: Disconnected'))
      .finally(() => setLoading(false))
  }, [])

  // --- 3. Handle Manual Form Submit (POST) ---
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiClient.post('/claims/', formData)
      setFormData({ policy_number: '', claim_amount: 0, description: '' })
      fetchClaims()
      alert("Claim created and sent to RabbitMQ!")
    } catch (err) {
      console.error(err)
      alert("Error creating claim. Check console.")
    }
  }

  // --- 4. Handle Delete Claim (DELETE) ---
  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this claim?")) return
    try {
      await apiClient.delete(`/claims/${id}`)
      setClaims(claims.filter(claim => claim.id !== id))
    } catch (err) {
      console.error("Delete failed:", err)
      alert("Could not delete claim.")
    }
  }

  // --- 5. Handle File Upload (AI Processing) ---
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setSelectedFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!selectedFile) return alert("Please select a file first")
    
    setUploading(true)
    const data = new FormData()
    data.append('file', selectedFile)

    try {
      await apiClient.post('/upload', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      alert("File uploaded! AI is generating embeddings...")
      setSelectedFile(null)
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      if (fileInput) fileInput.value = ''
    } catch (err) {
      alert("Upload failed.")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8">
      {/* Header */}
      <header className="max-w-6xl mx-auto mb-12 flex justify-between items-center text-white">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight">
            AI <span className="text-blue-500">Claims Processor</span>
          </h1>
          <p className="text-slate-400 mt-1">Vite + FastAPI + RabbitMQ + pgvector</p>
        </div>
        <div className={`px-4 py-1 rounded-full text-xs font-bold ${
          status.includes('Connected') ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
        }`}>
          {status}
        </div>
      </header>

      {/* Main Grid Layout Container */}
      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        
        {/* Left Column: Form Section */}
        <section className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl self-start">
          <h2 className="text-xl font-bold mb-6 text-white">Create New Claim</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Policy Number</label>
              <input 
                type="text" 
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 focus:outline-none focus:border-blue-500 transition-colors"
                value={formData.policy_number}
                onChange={(e) => setFormData({...formData, policy_number: e.target.value})}
                placeholder="e.g. POL-12345"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Amount ($)</label>
              <input 
                type="number" 
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 focus:outline-none focus:border-blue-500 transition-colors"
                value={formData.claim_amount}
                onChange={(e) => setFormData({...formData, claim_amount: parseFloat(e.target.value)})}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Description</label>
              <textarea 
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 h-24 focus:outline-none focus:border-blue-500 transition-colors"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Details for the AI to process..."
              />
            </div>

            {/* File Upload Section */}
            <div className="pt-4 border-t border-slate-700">
              <label className="block text-xs font-semibold text-slate-400 uppercase mb-2 text-blue-400">
                Attached Document (PDF/Text)
              </label>
              <input 
                type="file" 
                onChange={handleFileChange}
                className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-slate-700 file:text-white hover:file:bg-slate-600 cursor-pointer"
              />
              {selectedFile && (
                <button 
                  type="button"
                  onClick={handleUpload}
                  disabled={uploading}
                  className="mt-2 text-xs text-blue-400 hover:text-blue-300 font-medium underline"
                >
                  {uploading ? 'Processing AI...' : `Upload ${selectedFile.name} separately?`}
                </button>
              )}
            </div>

            <button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold text-white transition-all shadow-lg shadow-blue-500/20"
            >
              Submit to Queue
            </button>
          </form>
        </section>

        {/* Right Column: Refactored Structural Data Grid Table */}
        <section className="lg:col-span-2 bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl self-start w-full">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-white">Recent Records</h2>
            <button 
              onClick={fetchClaims} 
              className="text-sm text-blue-400 hover:text-blue-300 font-medium"
            >
              Refresh
            </button>
          </div>

          {/* Semantic Search Input Element */}
          <div className="mb-6">
            <div className="relative">
              <input 
                type="text" 
                placeholder="Semantic Search: e.g., 'car accidents in rain'..."
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 pl-10 focus:border-blue-500 outline-none text-white transition-all"
              />
              <svg className="absolute left-3 top-3.5 h-4 w-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          {/* Core Table Grid Block */}
          <div className="overflow-x-auto w-full">
            <table className="w-full border-collapse text-left text-xs text-slate-300">
              <thead>
                <tr className="border-b-2 border-slate-700 text-slate-400">
                  {/* Exact Column names matching Table: claims */}
                  <th className="p-3 font-monospace font-semibold tracking-wider">id</th>
                  <th className="p-3 font-monospace font-semibold tracking-wider">policy_number</th>
                  <th className="p-3 font-monospace font-semibold tracking-wider">claim_details</th>
                  <th className="p-3 font-monospace font-semibold tracking-wider">status</th>
                  {/* Exact Column names matching Table: document_chunks */}
                  <th className="p-3 font-monospace font-semibold tracking-wider text-blue-400">chunk_id</th>
                  <th className="p-3 font-monospace font-semibold tracking-wider text-blue-400">chunk_text</th>
                  <th className="p-3 font-monospace font-semibold tracking-wider text-blue-400">embedding_status</th>
                  <th className="p-3 text-right">actions</th>
                </tr>
              </thead>
              <tbody>
                {claims && claims.map((claim: any) => {
                  // Fallback safely if claims contain no sub-records yet
                  const documentsList = claim.documents && claim.documents.length > 0 
                    ? claim.documents 
                    : [{ id: 'NULL', filename: 'No text chunks', file_type: 'PENDING' }];

                  return documentsList.map((doc: any, index: number) => (
                    <tr 
                      key={`${claim.id}-${doc.id}-${index}`} 
                      className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                    >
                      {/* Claims Table Data Mapping */}
                      <td className="p-3 font-mono text-slate-400">{claim.id}</td>
                      <td className="p-3 font-medium text-white">{claim.policy_number}</td>
                      <td 
                        className="p-3 max-w-[120px] truncate" 
                        title={claim.claim_details || 'No description'}
                      >
                        {claim.claim_details || 'No description'}
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wide uppercase ${
                          claim.status === 'PROCESSED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                        }`}>
                          {claim.status}
                        </span>
                      </td>

                      {/* Document Chunks / Related Data Mapping */}
                      <td className="p-3 font-mono text-blue-400">{doc.id}</td>
                      <td 
                        className="p-3 max-w-[180px] truncate text-slate-400" 
                        title={doc.filename}
                      >
                        {doc.filename}
                      </td>
                      <td className="p-3">
                        <span className={`font-semibold ${
                          doc.file_type === 'COMPLETED' ? 'text-emerald-400' : 'text-amber-400'
                        }`}>
                          {doc.file_type}
                        </span>
                      </td>

                      {/* Row Destruction Event Trigger */}
                      <td className="p-3 text-right">
                        <button 
                          onClick={() => handleDelete(claim.id)}
                          className="text-red-400 hover:text-red-300 p-1 opacity-60 hover:opacity-100 transition-opacity" 
                          title="Delete Record"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ));
                })}
              </tbody>
            </table>
          </div>
        </section>

      </main>
    </div>
  )
}

export default App
