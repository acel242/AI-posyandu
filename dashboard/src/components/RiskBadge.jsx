export default function RiskBadge({ status }) {
  const styles = {
    green:      { background: '#22c55e', color: 'white' },
    yellow:     { background: '#eab308', color: '#1a1a1a' },
    red:        { background: '#ef4444', color: 'white' },
    unmeasured: { background: '#94a3b8', color: 'white' },
  }
  const labels = {
    green:      'Normal',
    yellow:     'Risiko',
    red:        'Buruk',
    unmeasured: 'Belum Diukur',
  }
  const icons = {
    green: '🟢',
    yellow: '🟡',
    red: '🔴',
    unmeasured: '⚪',
  }
  const s = styles[status] || styles.unmeasured
  return (
    <span style={{ ...s, padding: '2px 10px', borderRadius: 12, fontSize: 13, fontWeight: 'bold' }}>
      {icons[status] || '⚪'} {labels[status] || status}
    </span>
  )
}
