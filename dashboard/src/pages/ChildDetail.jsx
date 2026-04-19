import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import GrowthChart from '../components/GrowthChart'

function RiskBadge({ status }) {
  const colors = { green: '#4CAF50', yellow: '#FFC107', red: '#F44336', unmeasured: '#9E9E9E' }
  const labels = { green: 'Normal', yellow: 'Risiko', red: 'Buruk', unmeasured: 'Belum Diukur' }
  return (
    <span style={{
      background: colors[status] || '#9E9E9E',
      color: '#fff',
      padding: '2px 10px',
      borderRadius: 12,
      fontSize: 12,
      fontWeight: 600,
    }}>
      {labels[status] || status}
    </span>
  )
}

export default function ChildDetail({ onLogout }) {
  const { id } = useParams()
  const navigate = useNavigate()
  const [child, setChild] = useState(null)
  const [measurements, setMeasurements] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tab, setTab] = useState('chart') // chart | history

  useEffect(() => {
    loadData()
  }, [id])

  async function loadData() {
    setLoading(true)
    try {
      const res = await fetch(`/api/children/${id}/measurements`)
      const data = await res.json()
      if (data.error) { setError(data.error); return }
      setChild(data.child)
      setMeasurements(data.measurements || [])
    } catch (e) {
      setError('Gagal mengambil data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return (
    <div style={{ textAlign: 'center', padding: 60 }}>
      <div style={{ fontSize: 32, marginBottom: 12 }}>⏳</div>
      <p>Memuat...</p>
    </div>
  )

  if (error || !child) return (
    <div style={{ textAlign: 'center', padding: 60 }}>
      <p style={{ color: '#F44336' }}>{error || 'Data tidak ditemukan'}</p>
      <button onClick={() => navigate(-1)} className="btn btn-primary">Kembali</button>
    </div>
  )

  const validMeasurements = measurements.filter(m => m.age_months != null)
  const latest = validMeasurements[validMeasurements.length - 1]

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 20 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <button
          onClick={() => navigate(-1)}
          style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer', padding: 4 }}
        >
          ←
        </button>
        <div style={{ flex: 1 }}>
          <h2 style={{ margin: 0, color: '#1B5E20' }}>{child.name}</h2>
          <p style={{ margin: '4px 0 0', color: '#666', fontSize: 13 }}>
            {child.nik} • {child.gender === 'L' ? 'Laki-laki' : 'Perempuan'} • {child.date_of_birth}
          </p>
        </div>
        <RiskBadge status={latest?.overall_status || child.risk_status || 'unmeasured'} />
      </div>

      {/* Info cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
        {[
          { label: 'Orang Tua', value: child.parent_name },
          { label: 'Telepon', value: child.parent_phone },
          { label: 'Alamat', value: child.address },
          { label: 'Pengukuran', value: `${validMeasurements.length}x` },
        ].map(item => (
          <div key={item.label} style={{ background: '#f8f8f8', borderRadius: 10, padding: '12px' }}>
            <p style={{ margin: 0, fontSize: 10, color: '#888', textTransform: 'uppercase' }}>{item.label}</p>
            <p style={{ margin: '4px 0 0', fontWeight: 600, fontSize: 13 }}>{item.value || '-'}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 16, borderBottom: '2px solid #eee' }}>
        {[['chart', '📊 Growth Chart'], ['history', '📋 Riwayat']].map(([t, label]) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              fontWeight: tab === t ? 700 : 400,
              color: tab === t ? '#1B5E20' : '#888',
              borderBottom: tab === t ? '3px solid #1B5E20' : '3px solid transparent',
              borderRadius: '4px 4px 0 0',
              fontSize: 14,
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'chart' && (
        <GrowthChart child={child} measurements={validMeasurements} chartType="wfa" />
      )}

      {tab === 'history' && (
        <div style={{ background: '#fff', borderRadius: 16, overflow: 'hidden', boxShadow: '0 2px 12px rgba(0,0,0,0.08)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#f8f5f0' }}>
                {['Tanggal', 'Umur', 'Berat', 'Tinggi', 'Z BB/U', 'Z TB/U', 'Status'].map(h => (
                  <th key={h} style={{ padding: '10px 12px', textAlign: 'left', color: '#555' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {validMeasurements.slice().reverse().map((m, i) => {
                const status = m.overall_status || 'unmeasured'
                const statusColors = { green: '#4CAF50', yellow: '#FFC107', red: '#F44336', unmeasured: '#9E9E9E' }
                return (
                  <tr key={m.id || i} style={{ borderTop: '1px solid #f0f0f0' }}>
                    <td style={{ padding: '10px 12px' }}>{m.date || '-'}</td>
                    <td style={{ padding: '10px 12px' }}>{m.age_months ? `${Math.round(m.age_months)} bln` : '-'}</td>
                    <td style={{ padding: '10px 12px' }}>{m.weight_kg} kg</td>
                    <td style={{ padding: '10px 12px' }}>{m.height_cm} cm</td>
                    <td style={{ padding: '10px 12px', color: m.z_score_wfa != null ? (m.z_score_wfa >= -1 ? '#4CAF50' : m.z_score_wfa >= -2 ? '#FFC107' : '#F44336') : '#ccc' }}>
                      {m.z_score_wfa != null ? m.z_score_wfa.toFixed(2) : '-'}
                    </td>
                    <td style={{ padding: '10px 12px', color: m.z_score_hfa != null ? (m.z_score_hfa >= -1 ? '#4CAF50' : m.z_score_hfa >= -2 ? '#FFC107' : '#F44336') : '#ccc' }}>
                      {m.z_score_hfa != null ? m.z_score_hfa.toFixed(2) : '-'}
                    </td>
                    <td style={{ padding: '10px 12px' }}>
                      <span style={{ background: statusColors[status] || '#9E9E9E', color: '#fff', padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 600 }}>
                        {status === 'green' ? 'Normal' : status === 'yellow' ? 'Risiko' : status === 'red' ? 'Buruk' : '-'}
                      </span>
                    </td>
                  </tr>
                )
              })}
              {validMeasurements.length === 0 && (
                <tr><td colSpan={7} style={{ padding: 24, textAlign: 'center', color: '#999' }}>Belum ada data pengukuran.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
