import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [savedJobs, setSavedJobs] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiResults, setAiResults] = useState([])
  const [aiQuery, setAiQuery] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [tab, setTab] = useState('browse') // browse | ai | saved | resume
  const [resumeText, setResumeText] = useState('')
  const [jobDesc, setJobDesc] = useState('')
  const [resumeResult, setResumeResult] = useState(null)
  const [resumeLoading, setResumeLoading] = useState(false)
  const [fetchMsg, setFetchMsg] = useState('')
  const nav = useNavigate()

  useEffect(() => { loadJobs(); loadSaved() }, [])

  const logout = () => { localStorage.removeItem('token'); nav('/login') }

  const loadJobs = async (search = '') => {
    setLoading(true)
    try {
      const { data } = await api.get(`/jobs/${search ? `?search=${search}` : ''}`)
      setJobs(data)
    } catch { logout() }
    finally { setLoading(false) }
  }

  const loadSaved = async () => {
    try {
      const { data } = await api.get('/jobs/saved/')
      setSavedJobs(data)
    } catch {}
  }

  const saveJob = async (job) => {
    try {
      await api.post('/jobs/saved/', { job_id: job.id })
      loadSaved()
    } catch {}
  }

  const unsaveJob = async (savedId) => {
    try {
      await api.delete(`/jobs/saved/${savedId}/`)
      loadSaved()
    } catch {}
  }

  const runAiMatch = async () => {
    if (!aiQuery.trim()) return
    setAiLoading(true)
    setAiResults([])
    try {
      const { data } = await api.post('/jobs/ai/match/', { query: aiQuery, top_k: 10 })
      setAiResults(data)
    } catch (e) {
      setAiResults([{ error: e.response?.data?.error || 'AI service unavailable' }])
    } finally { setAiLoading(false) }
  }

  const analyzeResume = async () => {
    if (!resumeText.trim() || !jobDesc.trim()) return
    setResumeLoading(true)
    setResumeResult(null)
    try {
      const { data } = await api.post('/jobs/ai/resume/', {
        resume_text: resumeText,
        job_description: jobDesc,
      })
      setResumeResult(data)
    } catch { setResumeResult({ error: 'AI service unavailable' }) }
    finally { setResumeLoading(false) }
  }

  const triggerFetch = async () => {
    try {
      const { data } = await api.post('/jobs/fetch/', { role: query || 'developer' })
      setFetchMsg(data.message)
      setTimeout(() => setFetchMsg(''), 4000)
    } catch {}
  }

  const savedIds = new Set(savedJobs.map(s => s.job?.id))

  return (
    <div style={s.page}>
      <header style={s.header}>
        <h1 style={{ fontSize: 20 }}>AI Job Search</h1>
        <nav style={{ display: 'flex', gap: 8 }}>
          {['browse', 'ai', 'saved', 'resume'].map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ ...s.tabBtn, ...(tab === t ? s.tabActive : {}) }}>
              {t === 'browse' ? 'Browse' : t === 'ai' ? 'AI Match' : t === 'saved' ? `Saved (${savedJobs.length})` : 'Resume'}
            </button>
          ))}
        </nav>
        <button onClick={logout} style={s.logoutBtn}>Logout</button>
      </header>

      {tab === 'browse' && (
        <>
          <div style={s.searchBar}>
            <input style={s.searchInput} placeholder="Search jobs (e.g. Django remote)..."
              value={query} onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && loadJobs(query)} />
            <button style={s.btn} onClick={() => loadJobs(query)}>Search</button>
            <button style={{ ...s.btn, background: '#059669' }} onClick={triggerFetch} title="Fetch fresh jobs from Remotive">Fetch Jobs</button>
          </div>
          {fetchMsg && <p style={{ color: '#059669', padding: '0 0 12px' }}>{fetchMsg}</p>}
          {loading && <p style={s.center}>Loading...</p>}
          <div style={s.grid}>
            {jobs.map(job => (
              <JobCard key={job.id} job={job} saved={savedIds.has(job.id)}
                savedEntry={savedJobs.find(s => s.job?.id === job.id)}
                onSave={() => saveJob(job)}
                onUnsave={(id) => unsaveJob(id)} />
            ))}
            {!loading && jobs.length === 0 && <p style={s.empty}>No jobs found. Try fetching or a different search.</p>}
          </div>
        </>
      )}

      {tab === 'ai' && (
        <div style={{ padding: '20px 0' }}>
          <p style={{ color: '#555', marginBottom: 12 }}>Describe what you're looking for in natural language.</p>
          <div style={s.searchBar}>
            <input style={s.searchInput} placeholder="e.g. remote Django backend under 2 years exp"
              value={aiQuery} onChange={e => setAiQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && runAiMatch()} />
            <button style={s.btn} onClick={runAiMatch}>Match</button>
          </div>
          {aiLoading && <p style={s.center}>Running AI match...</p>}
          <div style={s.grid}>
            {aiResults.map((r, i) => r.error
              ? <p key={i} style={{ color: 'red' }}>{r.error}</p>
              : (
                <div key={i} style={s.card}>
                  <h3 style={{ fontSize: 16, marginBottom: 4 }}>{r.title}</h3>
                  <p style={s.company}>{r.company}</p>
                  <p style={s.location}>📍 {r.location}</p>
                  <div style={s.scoreBadge}>Match: {Math.round(r.score * 100)}%</div>
                  <p style={{ fontSize: 12, color: '#666', marginTop: 8 }}>{r.reason}</p>
                </div>
              )
            )}
          </div>
        </div>
      )}

      {tab === 'saved' && (
        <div style={{ padding: '20px 0' }}>
          {savedJobs.length === 0
            ? <p style={s.empty}>No saved jobs yet. Browse and save jobs you like.</p>
            : <div style={s.grid}>
              {savedJobs.map(s => (
                <JobCard key={s.id} job={s.job} saved={true} savedEntry={s}
                  onUnsave={(id) => unsaveJob(id)} />
              ))}
            </div>
          }
        </div>
      )}

      {tab === 'resume' && (
        <div style={{ padding: '20px 0', maxWidth: 800 }}>
          <p style={{ color: '#555', marginBottom: 16 }}>Paste your resume and a job description to get a match score and suggestions.</p>
          <textarea style={s.textarea} placeholder="Paste your resume text here..."
            value={resumeText} onChange={e => setResumeText(e.target.value)} rows={8} />
          <textarea style={{ ...s.textarea, marginTop: 12 }} placeholder="Paste the job description here..."
            value={jobDesc} onChange={e => setJobDesc(e.target.value)} rows={8} />
          <button style={{ ...s.btn, marginTop: 12 }} onClick={analyzeResume} disabled={resumeLoading}>
            {resumeLoading ? 'Analyzing...' : 'Analyze Match'}
          </button>
          {resumeResult && !resumeResult.error && (
            <div style={{ marginTop: 20, background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 6px #0001' }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: resumeResult.match_score >= 60 ? '#059669' : '#d97706' }}>
                {resumeResult.match_score}% Match
              </div>
              {resumeResult.suggestions.map((sg, i) => (
                <p key={i} style={{ marginTop: 8, color: '#444', fontSize: 14 }}>• {sg}</p>
              ))}
              {resumeResult.missing_keywords.length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <p style={{ fontSize: 13, color: '#888' }}>Missing keywords:</p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }}>
                    {resumeResult.missing_keywords.map(k => (
                      <span key={k} style={{ background: '#fef3c7', color: '#92400e', padding: '2px 8px', borderRadius: 12, fontSize: 12 }}>{k}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          {resumeResult?.error && <p style={{ color: 'red', marginTop: 12 }}>{resumeResult.error}</p>}
        </div>
      )}
    </div>
  )
}

function JobCard({ job, saved, savedEntry, onSave, onUnsave }) {
  if (!job) return null
  return (
    <div style={s.card}>
      <h3 style={{ fontSize: 16, marginBottom: 4 }}>{job.title}</h3>
      <p style={s.company}>{job.company}</p>
      <p style={s.location}>📍 {job.location}</p>
      {job.skills_required?.length > 0 && (
        <div style={s.tags}>
          {job.skills_required.slice(0, 5).map(sk => (
            <span key={sk} style={s.tag}>{sk}</span>
          ))}
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 }}>
        <a href={job.source_url} target="_blank" rel="noreferrer" style={s.link}>View Job →</a>
        {saved
          ? <button onClick={() => onUnsave(savedEntry?.id)} style={s.unsaveBtn}>Unsave</button>
          : <button onClick={onSave} style={s.saveBtn}>Save</button>
        }
      </div>
    </div>
  )
}
