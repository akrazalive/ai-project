import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

const GULF = ["UAE","Saudi Arabia","Qatar","Kuwait","Bahrain","Oman"]

export default function Dashboard() {
  const [countries, setCountries] = useState([])
  const [extraCountries, setExtraCountries] = useState([])
  const [role, setRole] = useState('')
  const [jobs, setJobs] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState('')
  const nav = useNavigate()

  useEffect(() => {
    api.get('/jobs/search/')
      .then(({ data }) => setCountries(data.countries.filter(c => !GULF.includes(c))))
      .catch(() => logout())
  }, [])

  const logout = () => { localStorage.removeItem('token'); nav('/login') }

  const toggle = (c) =>
    setExtraCountries(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c])

  const search = async () => {
    if (!role.trim()) { setError('Enter a job role'); return }
    setError('')
    setLoading(true)
    setJobs([])
    setQuery('')
    try {
      const { data } = await api.post('/jobs/search/', { role, countries: extraCountries })
      setJobs(data.jobs)
      setQuery(data.query)
      setSearched(true)
    } catch (e) {
      setError(e.response?.data?.error || 'Search failed')
    } finally { setLoading(false) }
  }

  const gulfJobs = jobs.filter(j => GULF.some(g => j.search_region?.includes(g)))
  const remoteJobs = jobs.filter(j => j.search_region === 'Worldwide Remote')
  const otherJobs = jobs.filter(j => !GULF.some(g => j.search_region?.includes(g)) && j.search_region !== 'Worldwide Remote')

  return (
    <div style={s.page}>
      <header style={s.header}>
        <span style={{ fontWeight: 700, fontSize: 18 }}>Job Search — LinkedIn</span>
        <button onClick={logout} style={s.logoutBtn}>Logout</button>
      </header>

      <div style={s.panel}>
        <div style={s.row}>
          <input style={s.roleInput}
            placeholder="Job role (e.g. Python Developer, React Engineer...)"
            value={role} onChange={e => setRole(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && search()} />
          <button style={s.searchBtn} onClick={search} disabled={loading}>
            {loading ? 'Searching...' : 'Search Jobs'}
          </button>
        </div>

        {error && <p style={s.error}>{error}</p>}

        <div style={s.alwaysOn}>
          <span style={s.badge('green')}>✓ All Gulf Countries</span>
          <span style={s.badge('blue')}>✓ Worldwide Remote</span>
          <span style={{ fontSize: 12, color: '#888' }}>— always searched, last 24 hrs</span>
        </div>

        <div style={s.countrySection}>
          <p style={s.label}>Also search in additional countries (optional)</p>
          <div style={s.countryGrid}>
            {countries.map(c => (
              <label key={c} style={s.chip(extraCountries.includes(c))}>
                <input type="checkbox" checked={extraCountries.includes(c)}
                  onChange={() => toggle(c)} style={{ marginRight: 6 }} />
                {c}
              </label>
            ))}
          </div>
          {extraCountries.length > 0 && (
            <button onClick={() => setExtraCountries([])} style={s.clearBtn}>Clear</button>
          )}
        </div>
      </div>

      {query && <p style={s.queryInfo}>Searched: <code style={s.code}>{query}</code></p>}
      {loading && <p style={s.center}>Fetching from LinkedIn...</p>}
      {searched && !loading && <p style={s.resultCount}>{jobs.length} jobs found in last 24 hrs</p>}

      {searched && !loading && jobs.length > 0 && (
        <>
          {gulfJobs.length > 0 && <Section title={`Gulf Countries (${gulfJobs.length})`} jobs={gulfJobs} />}
          {remoteJobs.length > 0 && <Section title={`Worldwide Remote (${remoteJobs.length})`} jobs={remoteJobs} />}
          {otherJobs.length > 0 && <Section title={`Other Countries (${otherJobs.length})`} jobs={otherJobs} />}
        </>
      )}

      {searched && !loading && jobs.length === 0 && (
        <p style={s.center}>No jobs found in the last 24 hrs. Try a broader role.</p>
      )}
    </div>
  )
}

function Section({ title, jobs }) {
  return (
    <div style={{ marginBottom: 32 }}>
      <h2 style={{ fontSize: 16, marginBottom: 12, color: '#374151' }}>{title}</h2>
      <div style={s.grid}>
        {jobs.map((job, i) => <JobCard key={i} job={job} />)}
      </div>
    </div>
  )
}

function JobCard({ job }) {
  const sourceColors = {
    LinkedIn:    { bg: '#dbeafe', color: '#1e40af' },
    NaukriGulf:  { bg: '#fef3c7', color: '#92400e' },
    Bayt:        { bg: '#d1fae5', color: '#065f46' },
    Indeed:      { bg: '#ede9fe', color: '#5b21b6' },
  }
  const sc = sourceColors[job.source] || { bg: '#f3f4f6', color: '#374151' }

  return (
    <div style={s.card}>
      {/* source badge + flag + time */}
      <div style={s.cardTop}>
        <span style={{ ...s.sourceBadge, background: sc.bg, color: sc.color }}>{job.source}</span>
        <span style={s.flag}>{job.flag}</span>
        {job.posted_ago && <span style={s.timeAgo}>{job.posted_ago}</span>}
      </div>

      <h3 style={s.jobTitle}>{job.title}</h3>
      <p style={s.company}>{job.company}</p>
      <p style={s.location}>📍 {job.location}</p>

      {job.applicants && <p style={s.applicants}>👥 {job.applicants}</p>}

      <div style={s.cardBottom}>
        {job.easy_apply ? (
          <a href={job.url} target="_blank" rel="noreferrer" style={s.easyApplyBtn}>⚡ Easy Apply</a>
        ) : (
          <a href={job.url} target="_blank" rel="noreferrer" style={s.externalBtn}>View Job →</a>
        )}
      </div>
    </div>
  )
}

const s = {
  page: { maxWidth: 1200, margin: '0 auto', padding: '0 16px 40px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 0', borderBottom: '1px solid #e5e7eb', marginBottom: 24 },
  logoutBtn: { background: 'none', border: '1px solid #ddd', padding: '6px 14px', borderRadius: 6, cursor: 'pointer' },
  panel: { background: '#fff', padding: 24, borderRadius: 10, boxShadow: '0 1px 6px #0001', marginBottom: 16 },
  row: { display: 'flex', gap: 10, marginBottom: 14 },
  roleInput: { flex: 1, padding: '10px 14px', border: '1px solid #ddd', borderRadius: 6, fontSize: 15 },
  searchBtn: { padding: '10px 24px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 15, whiteSpace: 'nowrap' },
  alwaysOn: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14, flexWrap: 'wrap' },
  badge: (color) => ({
    background: color === 'green' ? '#d1fae5' : '#dbeafe',
    color: color === 'green' ? '#065f46' : '#1e40af',
    padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 600,
  }),
  countrySection: { borderTop: '1px solid #f0f0f0', paddingTop: 14 },
  label: { fontSize: 13, fontWeight: 600, marginBottom: 10, color: '#555' },
  countryGrid: { display: 'flex', flexWrap: 'wrap', gap: 8 },
  chip: (active) => ({
    display: 'flex', alignItems: 'center', padding: '5px 12px',
    borderRadius: 20, border: `1px solid ${active ? '#2563eb' : '#ddd'}`,
    background: active ? '#eff6ff' : '#fff', color: active ? '#2563eb' : '#444',
    cursor: 'pointer', fontSize: 13, userSelect: 'none',
  }),
  clearBtn: { marginTop: 8, background: 'none', border: 'none', color: '#888', cursor: 'pointer', fontSize: 13, textDecoration: 'underline' },
  error: { color: '#dc2626', fontSize: 13 },
  center: { textAlign: 'center', color: '#888', padding: 32 },
  queryInfo: { fontSize: 12, color: '#888', marginBottom: 12 },
  code: { background: '#f3f4f6', padding: '2px 6px', borderRadius: 4 },
  resultCount: { color: '#374151', fontSize: 14, fontWeight: 600, marginBottom: 20 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 14 },

  // card
  card: { background: '#fff', padding: 16, borderRadius: 10, boxShadow: '0 1px 6px #0001', display: 'flex', flexDirection: 'column', gap: 6 },
  cardTop: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 },
  sourceBadge: { padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 600 },
  flag: { fontSize: 18 },
  location: { color: '#555', fontSize: 12, flex: 1 },
  timeAgo: { color: '#9ca3af', fontSize: 11, whiteSpace: 'nowrap' },
  jobTitle: { fontSize: 15, fontWeight: 600, lineHeight: 1.4, color: '#111' },
  company: { color: '#6b7280', fontSize: 13 },
  applicants: { color: '#6b7280', fontSize: 12 },
  cardBottom: { marginTop: 'auto', paddingTop: 10 },
  easyApplyBtn: {
    display: 'inline-block', padding: '6px 14px',
    background: '#2563eb', color: '#fff',
    borderRadius: 6, fontSize: 13, textDecoration: 'none', fontWeight: 600,
  },
  externalBtn: {
    display: 'inline-block', padding: '6px 14px',
    background: '#f3f4f6', color: '#374151',
    borderRadius: 6, fontSize: 13, textDecoration: 'none', fontWeight: 500,
    border: '1px solid #e5e7eb',
  },
}
