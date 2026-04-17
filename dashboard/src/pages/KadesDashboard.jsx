import { useState, useEffect } from 'react'

const API = '/api'

// Simple horizontal bar chart using divs — no recharts dependency
function DivBarChart({ data, title }) {
  const maxVal = Math.max(...data.map(d => d.value), 1)
  const colors = ['#dc3545', '#ffc107', '#28a745']

  return (
    <div style={styles.chartCard}>
      <h3 style={styles.chartTitle}>{title}</h3>
      {data.map((item, i) => {
        const pct = Math.round((item.value / maxVal) * 100)
        return (
          <div key={item.label} style={{ marginBottom: 14 }}>
            <div style={styles.chartLabel}>
              <span>{item.icon} {item.label}</span>
              <span style={{ fontWeight: 700 }}>{item.value} anak ({pct}%)</span>
            </div>
            <div style={styles.barTrack}>
              <div style={{
                ...styles.barFill,
                width: `${pct}%`,
                background: colors[i] || '#6f42c1',
                borderRadius: 6,
              }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Simple pie-like chart using nested divs
function DivPieChart({ data }) {
  const total = data.reduce((s, d) => s + d.value, 0)
  const colors = ['#dc3545', '#ffc107', '#28a745']

  return (
    <div style={styles.pieContainer}>
      {data.map((item, i) => {
        const pct = total > 0 ? Math.round((item.value / total) * 100) : 0
        return (
          <div key={item.label} style={styles.pieLegend}>
            <div style={{ ...styles.pieDot, background: colors[i] }} />
            <span style={{ fontSize: 14 }}>{item.icon} {item.label}</span>
            <span style={{ fontWeight: 700, marginLeft: 'auto' }}>{pct}%</span>
            <span style={{ color: '#6c757d', fontSize: 13, marginLeft: 8 }}>({item.value})</span>
          </div>
        )
      })}
      <div style={styles.pieTotal}>
        <span>Total</span>
        <span style={{ fontWeight: 700, fontSize: 18 }}>{total} anak</span>
      </div>
    </div>
  )
}

export default function KadesDashboard({ user, onLogout }) {
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, green: 0, yellow: 0, red: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const [childrenRes, statsRes] = await Promise.all([
          fetch(`${API}/children`),
          fetch(`${API}/stats`),
        ])
        if (!childrenRes.ok || !statsRes.ok) throw new Error(`HTTP error`)
        const childrenData = await childrenRes.json()
        const statsData = await statsRes.json()
        setChildren(childrenData)
        setStats(statsData)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // Derive stats from children if API stats not populated
  const derivedStats = {
    total: stats.total || children.length,
    green: stats.green ?? children.filter(c => ['green','hijau'].includes((c.risk_status||'').toLowerCase())).length,
    yellow: stats.yellow ?? children.filter(c => ['yellow','kuning'].includes((c.risk_status||'').toLowerCase())).length,
    red: stats.red ?? children.filter(c => ['red','merah'].includes((c.risk_status||'').toLowerCase())).length,
  }

  const coveragePct = derivedStats.total > 0
    ? Math.round(((derivedStats.green) / derivedStats.total) * 100) : 0

  const riskData = [
    { label: 'Merah (Gawat)', value: derivedStats.red, icon: '🔴' },
    { label: 'Kuning (Perlu Perhatian)', value: derivedStats.yellow, icon: '🟡' },
    { label: 'Hijau (Normal)', value: derivedStats.green, icon: '🟢' },
  ]

  const handleExport = () => {
    const headers = ['Nama', 'NIK', 'Orang Tua', 'Telepon', 'Alamat', 'RT/RW', 'Status Risiko', 'Terakhir Posyandu']
    const rows = children.map(c => [
      c.name || '-',
      c.nik || '-',
      c.parent_name || '-',
      c.parent_phone || '-',
      c.address || '-',
      c.rt_rw || '-',
      c.risk_status || 'green',
      c.last_posyandu_date || '-',
    ])
    const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `posyandu-export-${new Date().toISOString().slice(0,10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={styles.page}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.headerTitle}>🏘️ Posyandu AI — Kepala Desa</h1>
          <p style={styles.headerSub}>Selamat datang, <b>{user?.username}</b></p>
          <p style={{ margin: '2px 0 0', fontSize: 12, opacity: 0.75 }}>Desa Patakbanteng</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={handleExport} style={styles.exportBtn}>
            📥 Export CSV
          </button>
          <button onClick={onLogout} style={styles.logoutBtn}>Keluar</button>
        </div>
      </header>

      {/* Overview Cards */}
      <div style={styles.statsRow}>
        <div style={{ ...styles.statCard, borderLeft: '5px solid #28a745' }}>
          <div style={styles.statLabel}>🟢 Normal</div>
          <div style={styles.statValue}>{derivedStats.green}</div>
        </div>
        <div style={{ ...styles.statCard, borderLeft: '5px solid #ffc107' }}>
          <div style={styles.statLabel}>🟡 Perlu Perhatian</div>
          <div style={styles.statValue}>{derivedStats.yellow}</div>
        </div>
        <div style={{ ...styles.statCard, borderLeft: '5px solid #dc3545' }}>
          <div style={styles.statLabel}>🔴 Gawat</div>
          <div style={styles.statValue}>{derivedStats.red}</div>
        </div>
        <div style={{ ...styles.statCard, borderLeft: '5px solid #007bff' }}>
          <div style={styles.statLabel}>👶 Total Balita</div>
          <div style={styles.statValue}>{derivedStats.total}</div>
        </div>
        <div style={{ ...styles.statCard, borderLeft: '5px solid #17a2b8' }}>
          <div style={styles.statLabel}>📊 Cakupan Normal</div>
          <div style={styles.statValue}>{coveragePct}%</div>
        </div>
      </div>

      {/* Charts Row */}
      <div style={styles.chartsRow}>
        <DivBarChart data={riskData} title="📊 Distribusi Status Gizi Balita" />
        <DivPieChart data={riskData} />
      </div>

      {/* Detail Table */}
      <div style={styles.tableCard}>
        <h2 style={styles.tableTitle}>📋 Daftar Lengkap Balita Desa</h2>
        {loading && <p style={styles.loading}>Memuat data…</p>}
        {error && <p style={styles.errorText}>Gagal memuat: {error}</p>}
        {!loading && !error && children.length === 0 && (
          <p style={styles.empty}>Belum ada data balita terdaftar.</p>
        )}
        {!loading && children.length > 0 && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Nama Anak</th>
                  <th style={styles.th}>NIK</th>
                  <th style={styles.th}>Orang Tua</th>
                  <th style={styles.th}>Alamat / RT-RW</th>
                  <th style={styles.th}>Status</th>
                  <th style={styles.th}>Terakhir Posyandu</th>
                </tr>
              </thead>
              <tbody>
                {children.map((c) => {
                  const risk = (c.risk_status || c.risk || 'green').toLowerCase()
                  const isRed = risk === 'red' || risk === 'merah'
                  const isYellow = risk === 'yellow' || risk === 'kuning'
                  const badgeStyle = isRed
                    ? { background: '#f8d7da', color: '#721c24', border: '1.5px solid #dc3545' }
                    : isYellow
                    ? { background: '#fff3cd', color: '#856404', border: '1.5px solid #ffc107' }
                    : { background: '#d4edda', color: '#155724', border: '1.5px solid #28a745' }
                  const label = isRed ? 'Gawat' : isYellow ? 'Perlu Perhatian' : 'Normal'
                  return (
                    <tr key={c.id || c.name} style={styles.tr}>
                      <td style={styles.td}>{c.name || '-'}</td>
                      <td style={styles.td}>{c.nik || '-'}</td>
                      <td style={styles.td}>
                        <div>{c.parent_name || '-'}</div>
                        <div style={{ fontSize: 12, color: '#6c757d' }}>{c.parent_phone || '-'}</div>
                      </td>
                      <td style={styles.td}>
                        <div>{c.address || '-'}</div>
                        <div style={{ fontSize: 12, color: '#6c757d' }}>RT/RW {c.rt_rw || '-'}</div>
                      </td>
                      <td style={styles.td}>
                        <span style={{ ...badgeStyle, padding: '3px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, display: 'inline-block' }}>
                          {label}
                        </span>
                      </td>
                      <td style={styles.td}>{c.last_posyandu_date || 'Belum pernah'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    background: '#f0f2f5',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    padding: '0 0 40px',
  },
  header: {
    background: 'linear-gradient(135deg, #17a2b8, #6610f2)',
    color: '#fff',
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    flexWrap: 'wrap',
    gap: 12,
  },
  headerTitle: { margin: 0, fontSize: 18, fontWeight: 700 },
  headerSub: { margin: '4px 0 0', fontSize: 14, opacity: 0.9 },
  logoutBtn: {
    background: 'rgba(255,255,255,0.2)',
    border: '1px solid rgba(255,255,255,0.4)',
    color: '#fff',
    borderRadius: 8,
    padding: '8px 18px',
    cursor: 'pointer',
    fontSize: 14,
  },
  exportBtn: {
    background: 'rgba(255,255,255,0.9)',
    border: 'none',
    color: '#17a2b8',
    borderRadius: 8,
    padding: '8px 18px',
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: 600,
  },
  statsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: 12,
    padding: '20px 16px',
  },
  statCard: {
    background: '#fff',
    borderRadius: 12,
    padding: '16px 14px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  },
  statLabel: { fontSize: 13, color: '#6c757d', marginBottom: 6 },
  statValue: { fontSize: 28, fontWeight: 700, color: '#1a1a2e' },
  chartsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: 16,
    padding: '0 16px',
    marginBottom: 20,
  },
  chartCard: {
    background: '#fff',
    borderRadius: 12,
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  },
  chartTitle: {
    fontSize: 15,
    fontWeight: 700,
    margin: '0 0 16px',
    color: '#1a1a2e',
  },
  chartLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 13,
    color: '#333',
    marginBottom: 4,
  },
  barTrack: {
    height: 10,
    background: '#e9ecef',
    borderRadius: 6,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    transition: 'width 0.6s ease',
  },
  pieContainer: {
    background: '#fff',
    borderRadius: 12,
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  pieLegend: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    fontSize: 14,
  },
  pieDot: {
    width: 14,
    height: 14,
    borderRadius: '50%',
    flexShrink: 0,
  },
  pieTotal: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTop: '1px solid #e9ecef',
    paddingTop: 10,
    marginTop: 4,
    fontSize: 14,
    color: '#6c757d',
  },
  tableCard: {
    margin: '0 16px',
    background: '#fff',
    borderRadius: 12,
    padding: '16px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  },
  tableTitle: { fontSize: 16, fontWeight: 700, margin: '0 0 16px', color: '#1a1a2e' },
  tableWrap: { overflowX: 'auto', minWidth: 0 },
  table: { width: '100%', borderCollapse: 'collapse', minWidth: 600 },
  th: { textAlign: 'left', padding: '10px 14px', fontSize: 12, fontWeight: 600, color: '#6c757d', borderBottom: '2px solid #e9ecef', textTransform: 'uppercase', letterSpacing: 0.5 },
  tr: { borderBottom: '1px solid #f1f3f5' },
  td: { padding: '12px 14px', fontSize: 14, color: '#333' },
  loading: { color: '#6c757d', fontStyle: 'italic' },
  errorText: { color: '#dc3545' },
  empty: { color: '#6c757d', fontStyle: 'italic', textAlign: 'center', padding: 20 },
}
