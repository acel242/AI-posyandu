import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login({ onLogin }) {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) {
      setError('Username dan password harus diisi')
      return
    }
    setLoading(true)
    setError('')
    await new Promise(r => setTimeout(r, 400))
    const validUsers = {
      'bidan': { role: 'bidan', password: 'bidan123' },
      'kades': { role: 'kades', password: 'kades123' },
      'kader': { role: 'kader', password: 'kader123' },
      'admin': { role: 'kades', password: 'admin123' },
    }
    const lower = username.toLowerCase()
    const valid = validUsers[lower]
    if (valid && valid.password === password) {
      onLogin(username, valid.role)
      navigate(`/${valid.role}`)
    } else {
      setError('Username atau password salah')
    }
    setLoading(false)
  }

  return (
    <div className="login-page">
      <div className="login-card">
        {/* Logo */}
        <div className="login-logo">
          <div className="login-logo-icon">AI</div>
          <h1>AI Posyandu</h1>
          <p>Sistem Cerdas Posyandu Indonesia</p>
        </div>

        {error && (
          <div className="login-error">
            <span>⚠️</span> {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div>
            <label className="form-label">Username</label>
            <div className="login-input-wrap">
              <span className="input-icon">👤</span>
              <input
                className="form-input"
                type="text"
                placeholder="Masukkan username"
                value={username}
                onChange={e => setUsername(e.target.value)}
                autoComplete="username"
              />
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <label className="form-label">Password</label>
            <div className="login-input-wrap">
              <span className="input-icon">🔒</span>
              <input
                className="form-input"
                type={showPw ? 'text' : 'password'}
                placeholder="Masukkan password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="toggle-pw"
                onClick={() => setShowPw(v => !v)}
                title={showPw ? 'Sembunyikan' : 'Tampilkan'}
              >
                {showPw ? '🙈' : '👁'}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg btn-block"
            disabled={loading}
            style={{ marginTop: 24, fontWeight: 600, letterSpacing: '-0.01em' }}
          >
            {loading ? 'Memuat...' : 'Masuk'}
          </button>
        </form>

        <div className="login-footer">
          AI Posyandu © 2026
        </div>
      </div>
    </div>
  )
}
