// Vercel serverless function — proxies /api/* to backend tunnel
const BACKEND_URL = process.env.BACKEND_URL || 'https://tear-deliver-yacht-option.trycloudflare.com'

export default async function handler(req, res) {
  const url = new URL(req.url, 'http://localhost')

  try {
    // Collect body for POST/PUT/PATCH  
    let bodyData
    if (['POST', 'PUT', 'PATCH'].includes(req.method)) {
      const chunks = []
      for await (const chunk of req) chunks.push(chunk)
      bodyData = Buffer.concat(chunks)
    }

    // Build headers — filter out hop-by-hop headers
    const headers = {}
    for (const [k, v] of Object.entries(req.headers)) {
      const lk = k.toLowerCase()
      if (!['host', 'connection', 'transfer-encoding'].includes(lk)) {
        headers[k] = v
      }
    }

    const target = `${BACKEND_URL}${url.pathname}${url.search}`
    
    const resp = await fetch(target, {
      method: req.method,
      headers,
      body: bodyData,
    })

    const text = await resp.text()
    res.status(resp.status).setHeader('Content-Type', 'application/json; charset=utf-8').send(text)
  } catch (err) {
    console.error('[proxy]', err.message)
    res.status(502).json({ error: 'Backend unreachable', detail: err.message })
  }
}
