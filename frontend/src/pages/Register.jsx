import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'

export default function Register() {
  const [form, setForm] = useState({ email: '', username: '', password: '', preferred_role: '', preferred_location: '' })
  const [error, setError] = useState('')
  const nav = useNavigate()

  const submit = async e => {
    e.preventDefault()
    try {
      await axios.post('/api/users/register/', form)
      nav('/login')
    } catch (err) {
      setError(JSON.stringify(err.response?.data || 'Error'))
    }
  }

  const f = (k, v) => setForm({ ...form, [k]: v })

  return (
    <div style={styles.wrap}>
      <form onSubmit={submit} style={styles.card}>
        <h2>Create Account</h2>
        {error && <p style={styles.error}>{error}</p>}
        {[['email','Email','email'],['username','Username','text'],['password','Password','password'],
          ['preferred_role','Preferred Role (e.g. Backend Developer)','text'],
          ['preferred_location','Location (e.g. Remote)','text']].map(([k, ph, t]) => (
          <input key={k} style={styles.input} placeholder={ph} type={t}
            value={form[k]} onChange={e => f(k, e.target.value)} required={['email','username','password'].includes(k)} />
        ))}
        <button style={styles.btn} type="submit">Register</button>
        <p style={{ marginTop: 12, textAlign: 'center' }}>
          Have an account? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  )
}

const styles = {
  wrap: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' },
  card: { background: '#fff', padding: 32, borderRadius: 8, width: 380, boxShadow: '0 2px 12px #0001' },
  input: { display: 'block', width: '100%', padding: '10px 12px', margin: '8px 0', border: '1px solid #ddd', borderRadius: 6, fontSize: 14 },
  btn: { width: '100%', padding: '10px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', marginTop: 8, fontSize: 15 },
  error: { color: 'red', marginBottom: 8, fontSize: 12 },
}
