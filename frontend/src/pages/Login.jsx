import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const nav = useNavigate()

  const submit = async e => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await axios.post('/api/token/', form)
      localStorage.setItem('token', data.access)
      nav('/')
    } catch {
      setError('Invalid credentials. Admin access only.')
    }
  }

  return (
    <div style={s.wrap}>
      <form onSubmit={submit} style={s.card}>
        <h2 style={{ marginBottom: 6 }}>Job Search</h2>
        <p style={{ color: '#888', fontSize: 13, marginBottom: 20 }}>Admin access only</p>
        {error && <p style={s.error}>{error}</p>}
        <input style={s.input} placeholder="Username" autoFocus
          value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} required />
        <input style={s.input} placeholder="Password" type="password"
          value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required />
        <button style={s.btn} type="submit">Login</button>
      </form>
    </div>
  )
}

const s = {
  wrap: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' },
  card: { background: '#fff', padding: 32, borderRadius: 10, width: 340, boxShadow: '0 2px 16px #0002' },
  input: { display: 'block', width: '100%', padding: '10px 12px', margin: '8px 0', border: '1px solid #ddd', borderRadius: 6, fontSize: 14 },
  btn: { width: '100%', padding: 10, background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', marginTop: 8, fontSize: 15 },
  error: { color: '#dc2626', fontSize: 13, marginBottom: 10 },
}
