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
    // Simulate network delay for feel
    await new Promise(r => setTimeout(r, 500))
    // Dummy auth — check against known credentials
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
        <div className="login-logo">
          <div className="logo-icon">🏥</div>
          <h1>Posyandu Connect</h1>
        </div>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="login-input-wrap">
            <span className="input-icon">👤</span>
            <input
              className="form-input"
              type="text"
              placeholder="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>

          <div className="login-input-wrap">
            <span className="input-icon">🔒</span>
            <input
              className="form-input"
              type={showPw ? 'text' : 'password'}
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
            />
            <button type="button" className="toggle-pw" onClick={() => setShowPw(v => !v)}>
              {showPw ? '🙈' : '👁'}
            </button>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            style={{ marginTop: 20 }}
            disabled={loading}
          >
            {loading ? 'Memuat...' : 'MASUK'}
          </button>
        </form>
      </div>
    </div>
  )
}
