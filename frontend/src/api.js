const BASE = '/api'

export async function verifyFaces(fileA, fileB, threshold) {
  const fd = new FormData()
  fd.append('image_a', fileA)
  fd.append('image_b', fileB)
  fd.append('threshold', threshold)
  const r = await fetch(`${BASE}/verify`, { method: 'POST', body: fd })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function identifyFace(file, topK = 5) {
  const fd = new FormData()
  fd.append('image', file)
  fd.append('top_k', topK)
  const r = await fetch(`${BASE}/identify`, { method: 'POST', body: fd })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function enrollFace(name, file) {
  const fd = new FormData()
  fd.append('name', name)
  fd.append('image', file)
  const r = await fetch(`${BASE}/enroll`, { method: 'POST', body: fd })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function getEnrolled() {
  const r = await fetch(`${BASE}/enrolled`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function deleteEnrolled(name) {
  const r = await fetch(`${BASE}/enrolled/${encodeURIComponent(name)}`, { method: 'DELETE' })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function identifyEnrolled(file, topK = 5) {
  const fd = new FormData()
  fd.append('image', file)
  fd.append('top_k', topK)
  const r = await fetch(`${BASE}/identify-enrolled`, { method: 'POST', body: fd })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function getFairnessReport() {
  const r = await fetch(`${BASE}/fairness`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function getMetrics() {
  const r = await fetch(`${BASE}/metrics`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function sendChat(message, history) {
  const r = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function explainResult(contextType, data) {
  const r = await fetch(`${BASE}/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ context_type: contextType, data }),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function generateReport() {
  const r = await fetch(`${BASE}/report`, { method: 'POST' })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function processLivenessFrame(frameB64) {
  const r = await fetch(`${BASE}/liveness`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ frame_b64: frameB64 }),
  })
  if (!r.ok) return null
  return r.json()
}
