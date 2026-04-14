import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const nav = useNavigate()

  useEffect(() => { loadJobs() }, [])

  const loadJobs = async (search = '') => {
    setLoading(true)
    try {
      const { data } = await api.get(`/jobs/${search ? `?search=${search}` : ''}`)
      setJobs(data)
    } catch { logout() }
    finally { setLoading(false) }
  }

  const logout = () => { localStorage.removeItem('token'); nav('/login') }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={{ fontSize: 20 }}>AI Job Search</h1>
        <button onClick={logout} style={styles.logoutBtn}>Logout</button>
      </header>
      <div style={styles.searchBar}>
        <input style={styles.searchInput} placeholder="Search jobs (e.g. Django remote)..."
          value={query} onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && loadJobs(query)} />
        <button style={styles.searchBtn} onClick={() => loadJobs(query)}>Search</button>
      </div>
      {loading && <p style={{ textAlign: 'center', padding: 24 }}>Loading...</p>}
      <div style={styles.grid}>
        {jobs.map(job => (
          <div key={job.id} style={styles.card}>
            <h3 style={{ fontSize: 16, marginBottom: 4 }}>{job.title}</h3>
            <p style={styles.company}>{job.company}</p>
            <p style={styles.location}>📍 {job.location}</p>
            {job.skills_required?.length > 0 && (
              <div style={styles.tags}>
                {job.skills_required.slice(0, 5).map(s => (
                  <span key={s} style={styles.tag}>{s}</span>
                ))}
              </div>
            )}
            <a href={job.source_url} target="_blank" rel="noreferrer" style={styles.link}>
              View Job →
            </a>
          </div>
        ))}
        {!loading && jobs.length === 0 && (
          <p style={{ color: '#888', padding: 24 }}>No jobs found. Try a different search.</p>
        )}
      </div>
    </div>
  )
}

const styles = {
  page: { maxWidth: 1100, margin: '0 auto', padding: '0 16px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 0', borderBottom: '1px solid #eee' },
  logoutBtn: { background: 'none', border: '1px solid #ddd', padding: '6px 14px', borderRadius: 6, cursor: 'pointer' },
  searchBar: { display: 'flex', gap: 8, padding: '20px 0' },
  searchInput: { flex: 1, padding: '10px 14px', border: '1px solid #ddd', borderRadius: 6, fontSize: 15 },
  searchBtn: { padding: '10px 20px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16, paddingBottom: 32 },
  card: { background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 6px #0001' },
  company: { color: '#555', fontSize: 14, marginBottom: 4 },
  location: { color: '#888', fontSize: 13, marginBottom: 10 },
  tags: { display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 12 },
  tag: { background: '#eff6ff', color: '#2563eb', padding: '2px 8px', borderRadius: 12, fontSize: 12 },
  link: { color: '#2563eb', fontSize: 14, textDecoration: 'none' },
}
