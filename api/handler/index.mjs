import { readFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const distRoot = join(__dirname, '..', '..', 'dashboard', 'dist')

export default async function handler(req, res) {
  const url = new URL(req.url, 'http://localhost')
  
  // API proxy route
  if (url.pathname.startsWith('/api/')) {
    return fetch(`http://localhost:5001${url.pathname}${url.search}`).then(r => r.text()).then(body => {
      res.setHeader('Content-Type', 'application/json')
      return res.status(200).send(body)
    }).catch(() => res.status(502).send('Backend error'))
  }
  
  // Serve index.html for all non-file routes (SPA fallback)
  if (!url.pathname.includes('.')) {
    res.setHeader('Content-Type', 'text/html')
    return res.status(200).send(readFileSync(join(distRoot, 'index.html'), 'utf8'))
  }
  
  // Serve static assets
  const filePath = join(distRoot, url.pathname.slice(1))
  try {
    const content = readFileSync(filePath)
    const ext = filePath.split('.').pop()
    const types = { js: 'application/javascript', css: 'text/css', html: 'text/html' }
    res.setHeader('Content-Type', types[ext] || 'application/octet-stream')
    return res.status(200).send(content)
  } catch {
    // Fallback to index.html for SPA routing
    res.setHeader('Content-Type', 'text/html')
    return res.status(200).send(readFileSync(join(distRoot, 'index.html'), 'utf8'))
  }
}
