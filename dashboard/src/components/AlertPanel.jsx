/**
 * AlertPanel — slide-in notification history panel.
 * Props:
 *   isOpen     — boolean
 *   onClose    — callback
 *   alerts     — array of alert objects
 *   stats      — {sent, failed, pending}
 *   onRetry    — function(alertId)
 *   loading    — boolean
 */
import { useState, useEffect } from 'react'

const TYPE_LABELS = {
  posyandu_reminder: '📅 Reminder Posyandu',
  belum_timbang:     '⚠️ Belum Ditimbang',
  risiko_tinggi:     '🔴 Risiko Tinggi',
}
const TYPE_COLORS = {
  posyandu_reminder: '#3b82f6',
  belum_timbang:    '#f59e0b',
  risiko_tinggi:    '#ef4444',
}
const STATUS_ICONS = { sent: '✅', pending: '⏳', failed: '❌' }

function timeAgo(text) {
  if (!text) return '—'
  const diff = Date.now() - new Date(text).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1)  return 'baru saja'
  if (m < 60) return `${m}m lalu`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}jam lalu`
  const d = Math.floor(h / 24)
  return `${d}h lalu`
}

export default function AlertPanel({ isOpen, onClose, alerts, stats, onRetry, loading }) {
  const [activeTab, setActiveTab] = useState('all') // 'all' | 'failed'

  if (!isOpen) return null

  const filtered = activeTab === 'failed'
    ? alerts.filter(a => a.status === 'failed')
    : alerts

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.3)', zIndex: 40,
        }}
      />

      {/* Panel */}
      <div style={{
        position: 'fixed', top: 0, right: 0,
        width: '100%', maxWidth: 440,
        height: '100%', background: '#fff',
        boxShadow: '-4px 0 24px rgba(0,0,0,0.12)',
        zIndex: 50, display: 'flex', flexDirection: 'column',
        animation: 'slideInRight 0.2s ease',
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid #eee',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 17 }}>📊 Notifikasi</h2>
            {!loading && stats && (
              <p style={{ margin: '2px 0 0', fontSize: 12, color: '#888' }}>
                ✅ {stats.sent} terkirim  ·  ❌ {stats.failed} gagal  ·  ⏳ {stats.pending} pending
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none', fontSize: 20,
              cursor: 'pointer', padding: 4, borderRadius: 6,
            }}
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex', borderBottom: '1px solid #eee', flexShrink: 0,
        }}>
          {[['all', 'Semua'], ['failed', 'Gagal']].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              style={{
                flex: 1, padding: '10px 0',
                background: 'none', border: 'none',
                borderBottom: activeTab === key ? '2.5px solid #3b82f6' : '2.5px solid transparent',
                color: activeTab === key ? '#3b82f6' : '#888',
                fontWeight: activeTab === key ? 600 : 400,
                fontSize: 14, cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              {label}
              {key === 'failed' && stats?.failed > 0 && (
                <span style={{
                  marginLeft: 4, background: '#ef4444', color: '#fff',
                  borderRadius: 10, fontSize: 10, padding: '0 5px',
                }}>
                  {stats.failed}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0' }}>
          {loading ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>Memuat...</div>
          ) : filtered.length === 0 ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>
              {activeTab === 'failed' ? 'Tidak ada notifikasi gagal ✅' : 'Belum ada notifikasi'}
            </div>
          ) : (
            filtered.map(alert => (
              <AlertItem
                key={alert.id}
                alert={alert}
                onRetry={onRetry}
              />
            ))
          )}
        </div>

        {/* Footer */}
        {!loading && alerts.length > 0 && (
          <div style={{
            padding: '12px 20px', borderTop: '1px solid #eee',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <span style={{ fontSize: 12, color: '#888' }}>
              Menampilkan {filtered.length} dari {alerts.length}
            </span>
            <button
              onClick={onClose}
              style={{
                background: '#3b82f6', color: '#fff',
                border: 'none', borderRadius: 8, padding: '7px 16px',
                fontSize: 13, cursor: 'pointer',
              }}
            >
              Tutup
            </button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); }
          to   { transform: translateX(0); }
        }
      `}</style>
    </>
  )
}

function AlertItem({ alert, onRetry }) {
  const color = TYPE_COLORS[alert.alert_type] || '#6b7280'
  const label  = TYPE_LABELS[alert.alert_type]  || alert.alert_type

  return (
    <div style={{
      margin: '4px 12px',
      border: '1px solid',
      borderColor: alert.status === 'failed' ? '#fca5a5' : '#e5e7eb',
      borderRadius: 10, padding: '10px 12px',
      background: alert.status === 'failed' ? '#fef2f2' : '#fff',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 12, fontWeight: 600, color, whiteSpace: 'nowrap' }}>{label}</span>
          <span style={{ fontSize: 11, color: '#888' }}>
            {STATUS_ICONS[alert.status] || '•'} {alert.status}
          </span>
        </div>
        {alert.status === 'failed' && onRetry && (
          <button
            onClick={() => onRetry(alert.id)}
            style={{
              background: '#3b82f6', color: '#fff',
              border: 'none', borderRadius: 6, padding: '3px 10px',
              fontSize: 11, cursor: 'pointer',
            }}
          >
            🔄 Retry
          </button>
        )}
      </div>

      {alert.message_text && (
        <p style={{ margin: '4px 0 0', fontSize: 12, color: '#374151', whiteSpace: 'pre-wrap' }}>
          {alert.message_text.slice(0, 120)}{alert.message_text.length > 120 ? '…' : ''}
        </p>
      )}
      <p style={{ margin: '3px 0 0', fontSize: 11, color: '#9ca3af' }}>
        {timeAgo(alert.sent_time || alert.created_at)}
        {alert.recipient_telegram_id && ` · KE ${alert.recipient_telegram_id}`}
      </p>
    </div>
  )
}
