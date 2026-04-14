import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

const Guard = ({ children }) =>
  localStorage.getItem('token') ? children : <Navigate to="/login" />

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Guard><Dashboard /></Guard>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
