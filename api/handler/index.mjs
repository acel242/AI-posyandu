// Single entry point: serves SPA + proxies /api/*
import { readFileSync } from 'fs'
import { join, extname, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = join(__dirname, '..', '..')
const DIST = join(ROOT, 'dashboard', 'dist')

const BACKEND_URL = process.env.BACKEND_URL || 'https://tear-deliver-yacht-option.trycloudflare.com'

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
}

export default async function handler(req, res) {
  const pathname = new URL(req.url).pathname

  // ── API Proxy ───────────────────────────────────────────────
  if (pathname.startsWith('/api/')) {
    try {
      let body
      if (['POST', 'PUT', 'PATCH'].includes(req.method)) {
        const chunks = []
        for await (const chunk of req) chunks.push(chunk)
        body = Buffer.concat(chunks)
      }

      const headers = {}
      for (const [k, v] of Object.entries(req.headers)) {
        const lk = k.toLowerCase()
        if (!['host', 'connection', 'transfer-encoding'].includes(lk)) {
          headers[k] = v
        }
      }

      const target = `${BACKEND_URL}${pathname}${req.url.includes('?') ? '?' + req.url.split('?', 2)[1] : ''}`
      const resp = await fetch(target, { method: req.method, headers, body })
      const text = await resp.text()
      return res.status(resp.status).setHeader('Content-Type', 'application/json').send(text)
    } catch (e) {
      console.error('[proxy]', e.message)
      return res.status(502).json({ error: 'Backend unreachable' })
    }
  }

  // ── Static Asset ────────────────────────────────────────────
  const ext = extname(pathname)
  if (ext && MIME_TYPES[ext]) {
    try {
      const filePath = join(DIST, pathname.slice(1))
      const content = readFileSync(filePath)
      res.setHeader('Content-Type', MIME_TYPES[ext])
      return res.status(200).send(content)
    } catch (_) { /* fall through to SPA fallback */ }
  }

  // ── SPA Fallback ────────────────────────────────────────────
  try {
    const html = readFileSync(join(DIST, 'index.html'), 'utf-8')
    res.setHeader('Content-Type', 'text/html; charset=utf-8')
    return res.status(200).send(html)
  } catch (e) {
    return res.status(500).send(`Static files not found: ${DIST}\n${e.message}`)
  }
}
