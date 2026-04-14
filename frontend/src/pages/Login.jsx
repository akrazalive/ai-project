import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const nav = useNavigate()

  const submit = async e => {
    e.preventDefault()
    try {
      const { data } = await axios.post('/api/auth/token/', form)
      localStorage.setItem('token', data.access)
      nav('/')
    } catch {
      setError('Invalid credentials')
    }
  }

  return (
    <div style={styles.wrap}>
      <form onSubmit={submit} style={styles.card}>
        <h2>AI Job Search</h2>
        <p style={{ color: '#666', marginBottom: 16 }}>Sign in to your account</p>
        {error && <p style={styles.error}>{error}</p>}
        <input style={styles.input} placeholder="Email" type="email"
          value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required />
        <input style={styles.input} placeholder="Password" type="password"
          value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required />
        <button style={styles.btn} type="submit">Login</button>
        <p style={{ marginTop: 12, textAlign: 'center' }}>
          No account? <Link to="/register">Register</Link>
        </p>
      </form>
    </div>
  )
}

const styles = {
  wrap: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' },
  card: { background: '#fff', padding: 32, borderRadius: 8, width: 360, boxShadow: '0 2px 12px #0001' },
  input: { display: 'block', width: '100%', padding: '10px 12px', margin: '8px 0', border: '1px solid #ddd', borderRadius: 6, fontSize: 14 },
  btn: { width: '100%', padding: '10px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', marginTop: 8, fontSize: 15 },
  error: { color: 'red', marginBottom: 8 },
}
