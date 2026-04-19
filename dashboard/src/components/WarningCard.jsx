export default function WarningCard({ count }) {
  if (count === 0) return null
  return (
    <div className="warning-card">
      <span className="icon">⚠️</span>
      <span>
        <strong>{count} anak</strong> belum ditimbang lebih dari 30 hari
      </span>
    </div>
  )
}
