import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login({ onLogin, user }) {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')

  // If already logged in, redirect to role dashboard
  useEffect(() => {
    if (user?.role) {
      navigate(`/${user.role}`, { replace: true })
    }
  }, [user, navigate])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!username.trim()) {
      setError('Masukkan nama pengguna')
      return
    }
    onLogin(username.trim())
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.logo}>🩺</div>
        <h1 style={styles.title}>Posyandu AI</h1>
        <p style={styles.subtitle}>Masuk ke Dashboard</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Nama Pengguna</label>
          <input
            type="text"
            value={username}
            onChange={(e) => { setUsername(e.target.value); setError('') }}
            placeholder="Contoh: bidan_sari, kader_ani, kades_budi"
            style={styles.input}
          />
          {error && <p style={styles.error}>{error}</p>}

          <button type="submit" style={styles.button}>
            Masuk
          </button>
        </form>

        <div style={styles.hints}>
          <p style={styles.hintTitle}>Petunjuk peran:</p>
          <p style={styles.hint}>• Nama mengandung <b>"bidan"</b> → Dashboard Bidan</p>
          <p style={styles.hint}>• Nama mengandung <b>"kades"</b> → Dashboard Kepala Desa</p>
          <p style={styles.hint}>• Lainnya → Dashboard Kader</p>
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  card: {
    background: '#fff',
    borderRadius: 16,
    padding: '40px 36px',
    width: '100%',
    maxWidth: 420,
    boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
  },
  logo: {
    fontSize: 48,
    textAlign: 'center',
    marginBottom: 8,
  },
  title: {
    textAlign: 'center',
    fontSize: 28,
    fontWeight: 700,
    color: '#1a1a2e',
    margin: '0 0 4px',
  },
  subtitle: {
    textAlign: 'center',
    color: '#6c757d',
    marginBottom: 28,
    fontSize: 15,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: 600,
    color: '#333',
    marginBottom: 4,
  },
  input: {
    padding: '12px 16px',
    borderRadius: 10,
    border: '1.5px solid #dee2e6',
    fontSize: 15,
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  button: {
    marginTop: 12,
    padding: '12px',
    borderRadius: 10,
    border: 'none',
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: '#fff',
    fontSize: 16,
    fontWeight: 600,
    cursor: 'pointer',
  },
  error: {
    color: '#dc3545',
    fontSize: 13,
    margin: 0,
  },
  hints: {
    marginTop: 24,
    padding: '14px 16px',
    background: '#f8f9fa',
    borderRadius: 10,
  },
  hintTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: '#495057',
    margin: '0 0 6px',
  },
  hint: {
    fontSize: 12,
    color: '#6c757d',
    margin: '2px 0',
  },
}
