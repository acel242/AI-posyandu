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
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0D3B20 0%, #166534 50%, #1B5E20 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
    }}>
      <div style={{
        background: 'white',
        borderRadius: 20,
        padding: '44px 36px',
        width: '100%',
        maxWidth: 420,
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{
            width: 72, height: 72,
            borderRadius: '50%',
            background: '#0D3B20',
            margin: '0 auto 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.6rem',
            fontWeight: 700,
            color: 'white',
          }}>
            AI
          </div>
          <h1 style={{
            fontSize: '1.6rem',
            fontWeight: 700,
            color: '#0D3B20',
            margin: 0,
            letterSpacing: '-0.02em',
          }}>
            AI Posyandu
          </h1>
          <p style={{
            fontSize: '0.85rem',
            color: '#6B7280',
            margin: '6px 0 0',
          }}>
            Sistem Cerdas Posyandu
          </p>
        </div>

        {error && (
          <div style={{
            background: '#FEF2F2',
            color: '#991B1B',
            padding: '10px 14px',
            borderRadius: 10,
            fontSize: '0.85rem',
            marginBottom: 18,
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{
              display: 'block',
              fontSize: '0.78rem',
              fontWeight: 600,
              color: '#374151',
              marginBottom: 6,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            }}>
              Username
            </label>
            <input
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '1.5px solid #E5E7EB',
                borderRadius: 10,
                fontSize: '0.95rem',
                color: '#1F2937',
                transition: 'border-color 0.15s, box-shadow 0.15s',
              }}
              type="text"
              placeholder="Masukkan username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onFocus={e => { e.target.style.borderColor = '#16A34A'; e.target.style.boxShadow = '0 0 0 3px rgba(22,163,74,0.1)' }}
              onBlur={e => { e.target.style.borderColor = '#E5E7EB'; e.target.style.boxShadow = 'none' }}
              autoComplete="username"
            />
          </div>

          <div style={{ marginBottom: 24 }}>
            <label style={{
              display: 'block',
              fontSize: '0.78rem',
              fontWeight: 600,
              color: '#374151',
              marginBottom: 6,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  paddingRight: 44,
                  border: '1.5px solid #E5E7EB',
                  borderRadius: 10,
                  fontSize: '0.95rem',
                  color: '#1F2937',
                  transition: 'border-color 0.15s, box-shadow 0.15s',
                }}
                type={showPw ? 'text' : 'password'}
                placeholder="Masukkan password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                onFocus={e => { e.target.style.borderColor = '#16A34A'; e.target.style.boxShadow = '0 0 0 3px rgba(22,163,74,0.1)' }}
                onBlur={e => { e.target.style.borderColor = '#E5E7EB'; e.target.style.boxShadow = 'none' }}
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPw(v => !v)}
                style={{
                  position: 'absolute',
                  right: 12,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#9CA3AF',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  padding: 4,
                }}
              >
                {showPw ? '🙈' : '👁'}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '13px',
              borderRadius: 10,
              border: 'none',
              background: loading ? '#6B7280' : '#0D3B20',
              color: 'white',
              fontSize: '1rem',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background 0.2s, transform 0.1s',
              letterSpacing: '-0.01em',
            }}
            onMouseDown={e => { if (!loading) e.currentTarget.style.transform = 'scale(0.98)' }}
            onMouseUp={e => { e.currentTarget.style.transform = 'scale(1)' }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)' }}
          >
            {loading ? 'Memuat...' : 'Masuk'}
          </button>
        </form>

        <div style={{
          textAlign: 'center',
          marginTop: 28,
          paddingTop: 20,
          borderTop: '1px solid #F3F4F6',
          fontSize: '0.75rem',
          color: '#9CA3AF',
        }}>
          AI Posyandu © 2026
        </div>
      </div>
    </div>
  )
}
