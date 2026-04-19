import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Login from './pages/Login'
import KaderDashboard from './pages/KaderDashboard'
import BidanDashboard from './pages/BidanDashboard'
import KadesDashboard from './pages/KadesDashboard'
import AlertPanel from './components/AlertPanel'

function ProtectedRoute({ role, allowedRole, children }) {
  if (role !== allowedRole) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const [user, setUser] = useState(() => {
    const saved = sessionStorage.getItem('posyandu_auth')
    return saved ? JSON.parse(saved) : null
  })
  const [alertPanelOpen, setAlertPanelOpen] = useState(false)
  const [alertData, setAlertData] = useState({ alerts: [], stats: {}, loading: true })

  const login = (username, role) => {
    const newUser = { username, role }
    sessionStorage.setItem('posyandu_auth', JSON.stringify(newUser))
    setUser(newUser)
  }

  const logout = () => {
    sessionStorage.removeItem('posyandu_auth')
    setUser(null)
  }

  const handleBellClick = async () => {
    setAlertPanelOpen(true)
    setAlertData(d => ({ ...d, loading: true }))
    try {
      const [logsRes, statsRes] = await Promise.all([
        fetch('/api/alerts/logs?limit=100'),
        fetch('/api/alerts/stats'),
      ])
      const logs = await logsRes.json()
      const stats = await statsRes.json()
      setAlertData({ alerts: Array.isArray(logs) ? logs : [], stats, loading: false })
    } catch {
      setAlertData({ alerts: [], stats: {}, loading: false })
    }
  }

  const handleRetry = async (alertId) => {
    await fetch(`/api/alerts/retry/${alertId}`, { method: 'POST' })
    handleBellClick() // refresh
  }

  return (
    <BrowserRouter>
      {alertPanelOpen && (
        <AlertPanel
          isOpen={alertPanelOpen}
          onClose={() => setAlertPanelOpen(false)}
          alerts={alertData.alerts}
          stats={alertData.stats}
          onRetry={handleRetry}
          loading={alertData.loading}
        />
      )}
      <Routes>
        <Route path="/login" element={<Login onLogin={login} />} />
        <Route
          path="/kader"
          element={
            <ProtectedRoute role={user?.role} allowedRole="kader">
              <KaderDashboard user={user} onLogout={logout} onBellClick={handleBellClick} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/bidan"
          element={
            <ProtectedRoute role={user?.role} allowedRole="bidan">
              <BidanDashboard user={user} onLogout={logout} onBellClick={handleBellClick} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/kades"
          element={
            <ProtectedRoute role={user?.role} allowedRole="kades">
              <KadesDashboard user={user} onLogout={logout} onBellClick={handleBellClick} />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
