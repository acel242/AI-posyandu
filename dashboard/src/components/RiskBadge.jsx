export default function RiskBadge({ status }) {
  const styles = {
    green:      { background: '#DCFCE7', color: '#15803d' },
    yellow:     { background: '#fef3c7', color: '#92400E' },
    red:        { background: '#fef2f2', color: '#991B1B' },
    unmeasured: { background: '#F1F5F9', color: '#475569' },
  }
  const labels = {
    green:      'Normal',
    yellow:     'Risiko',
    red:        'Rujuk',
    unmeasured: 'Belum Diukur',
  }
  const icons = {
    green:      '🟢',
    yellow:     '🟡',
    red:        '🔴',
    unmeasured: '⚪',
  }
  const s = styles[status] || styles.unmeasured
  const label = labels[status] || status || 'Unknown'
  const icon = icons[status] || '⚪'

  return (
    <span
      className="badge"
      style={{
        background: s.background,
        color: s.color,
      }}
    >
      {icon} {label}
    </span>
  )
}
