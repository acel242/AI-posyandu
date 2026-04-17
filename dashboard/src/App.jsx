import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Login from './pages/Login'
import KaderDashboard from './pages/KaderDashboard'
import BidanDashboard from './pages/BidanDashboard'
import KadesDashboard from './pages/KadesDashboard'

function ProtectedRoute({ role, allowedRole, children }) {
  if (role !== allowedRole) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const [user, setUser] = useState(() => {
    const saved = sessionStorage.getItem('posyandu_auth')
    return saved ? JSON.parse(saved) : null
  })

  const login = (username) => {
    let role = 'kader'
    const lower = username.toLowerCase()
    if (lower.includes('bidan')) role = 'bidan'
    else if (lower.includes('kades')) role = 'kades'
    const newUser = { username, role }
    sessionStorage.setItem('posyandu_auth', JSON.stringify(newUser))
    setUser(newUser)
  }

  const logout = () => {
    sessionStorage.removeItem('posyandu_auth')
    setUser(null)
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login onLogin={login} user={user} />} />
        <Route
          path="/kader"
          element={
            <ProtectedRoute role={user?.role} allowedRole="kader">
              <KaderDashboard user={user} onLogout={logout} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/bidan"
          element={
            <ProtectedRoute role={user?.role} allowedRole="bidan">
              <BidanDashboard user={user} onLogout={logout} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/kades"
          element={
            <ProtectedRoute role={user?.role} allowedRole="kades">
              <KadesDashboard user={user} onLogout={logout} />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
