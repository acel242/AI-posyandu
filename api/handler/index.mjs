// Vercel API handler — serves SPA + proxies /api/* to backend
import { readFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const distRoot = join(__dirname, '..', '..', 'dashboard', 'dist')

// Backend URL — override via BACKEND_URL env var
const BACKEND_URL = process.env.BACKEND_URL || 'https://tear-deliver-yacht-option.trycloudflare.com'

export default async function handler(req, res) {
  const url = new URL(req.url, 'http://localhost')

  // ── API Proxy ───────────────────────────────────────────────
  if (url.pathname.startsWith('/api/')) {
    try {
      const target = `${BACKEND_URL}${url.pathname}${url.search}`
      console.log(`[proxy] ${req.method} → ${target}`)

      const headers = {}
      req.headers.forEach((v, k) => {
        if (!['host','connection','transfer-encoding'].includes(k.toLowerCase()))
          headers[k] = v
      })

      const bodyBuf = []
      for await (const chunk of req) bodyBuf.push(chunk)

      const resp = await fetch(target, {
        method: req.method,
        headers,
        body: ['POST','PUT','PATCH'].includes(req.method) ? Buffer.concat(bodyBuf) : undefined,
      })

      const text = await resp.text()
      res.status(resp.status)
      res.set('Content-Type', 'application/json; charset=utf-8')
      res.send(text)
    } catch (err) {
      console.error('[proxy] error:', err.message)
      res.status(502).json({ error: 'Backend unreachable', detail: err.message })
    }
    return
  }

  // ── Static Asset ────────────────────────────────────────────
  if (url.pathname.includes('.')) {
    const filePath = join(distRoot, url.pathname.slice(1))
    try {
      const content = readFileSync(filePath)
      const ext = filePath.split('.').pop().toLowerCase()
      const mime = {
        js:'application/javascript; charset=utf-8', css:'text/css; charset=utf-8',
        html:'text/html; charset=utf-8', json:'application/json; charset=utf-8',
        png:'image/png', jpg:'image/jpeg', svg:'image/svg+xml',
        woff:'font/woff', woff2:'font/woff2',
      }
      res.set('Content-Type', mime[ext] || 'application/octet-stream')
      return res.status(200).send(content)
    } catch (_) { /* fall through */ }
  }

  // ── SPA Fallback ────────────────────────────────────────────
  res.set('Content-Type', 'text/html; charset=utf-8')
  return res.status(200).send(readFileSync(join(distRoot, 'index.html'), 'utf-8'))
}
