import { useState, useCallback, useEffect } from 'react'
import { enrollFace, getEnrolled, deleteEnrolled, identifyEnrolled } from '../api'

function DropZone({ file, onFile, compact }) {
  const [drag, setDrag] = useState(false)
  const preview = file ? URL.createObjectURL(file) : null

  const handleDrop = useCallback(e => {
    e.preventDefault(); setDrag(false)
    const f = e.dataTransfer.files[0]
    if (f?.type.startsWith('image/')) onFile(f)
  }, [onFile])

  const borderColor = drag ? 'rgba(0,229,255,0.55)' : file ? 'rgba(0,229,255,0.28)' : 'rgba(255,255,255,0.08)'

  return (
    <label style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      gap: 12, cursor: 'pointer', borderRadius: 14,
      minHeight: compact ? 180 : 240,
      background: drag ? 'rgba(0,229,255,0.04)' : 'rgba(16,25,50,0.7)',
      border: `1px solid ${borderColor}`,
      boxShadow: drag ? '0 0 50px rgba(0,229,255,0.1), inset 0 0 30px rgba(0,229,255,0.03)' : 'none',
      position: 'relative', overflow: 'hidden',
      transition: 'all 0.22s ease',
    }}
    onDragOver={e => { e.preventDefault(); setDrag(true) }}
    onDragLeave={() => setDrag(false)}
    onDrop={handleDrop}>
      <input type="file" accept="image/*" style={{ display: 'none' }}
        onChange={e => e.target.files[0] && onFile(e.target.files[0])} />

      {[['top','left'], ['top','right'], ['bottom','left'], ['bottom','right']].map(([v, h]) => (
        <div key={`${v}${h}`} style={{
          position: 'absolute', [v]: 9, [h]: 9, width: 14, height: 14,
          borderTop: v === 'top' ? `2px solid rgba(0,229,255,${file ? 0.45 : 0.22})` : 'none',
          borderBottom: v === 'bottom' ? `2px solid rgba(0,229,255,${file ? 0.45 : 0.22})` : 'none',
          borderLeft: h === 'left' ? `2px solid rgba(0,229,255,${file ? 0.45 : 0.22})` : 'none',
          borderRight: h === 'right' ? `2px solid rgba(0,229,255,${file ? 0.45 : 0.22})` : 'none',
        }} />
      ))}

      {preview ? (
        <img src={preview} alt="face" style={{
          maxWidth: '85%', maxHeight: 190, borderRadius: 10,
          objectFit: 'contain', boxShadow: '0 6px 28px rgba(0,0,0,0.6)',
        }} />
      ) : (
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: compact ? 22 : 28, color: 'rgba(0,229,255,0.2)',
            marginBottom: 10,
          }}>⊞</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            <span style={{ color: 'var(--accent)', fontWeight: 700 }}>Click</span> or drag face photo
          </div>
        </div>
      )}
    </label>
  )
}

function IdentityCard({ name, onDelete }) {
  const initials = name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
  const hue = [...name].reduce((h, c) => h + c.charCodeAt(0), 0) % 360
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px',
      background: 'linear-gradient(135deg, rgba(22,34,62,0.92), rgba(14,22,46,0.96))',
      border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 12, transition: 'all 0.18s ease',
    }}
    onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(0,229,255,0.18)'; e.currentTarget.style.transform = 'translateX(3px)' }}
    onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; e.currentTarget.style.transform = '' }}>
      <div style={{
        width: 38, height: 38, borderRadius: 11, flexShrink: 0,
        background: `hsl(${hue},55%,18%)`,
        border: `1px solid hsl(${hue},55%,32%)`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 12, fontWeight: 800,
        color: `hsl(${hue},75%,68%)`,
        boxShadow: `0 0 14px hsl(${hue},60%,30%)33`,
      }}>{initials || '?'}</div>
      <div style={{ flex: 1, fontSize: 13, fontWeight: 600, color: 'var(--text-pri)', letterSpacing: '0.01em' }}>
        {name}
      </div>
      <button onClick={() => onDelete(name)} style={{
        background: 'rgba(244,63,94,0.07)', border: '1px solid rgba(244,63,94,0.2)',
        borderRadius: 7, padding: '4px 10px', cursor: 'pointer',
        color: 'var(--danger)', fontSize: 10, fontWeight: 700, letterSpacing: '0.04em',
        textTransform: 'uppercase',
        transition: 'all 0.15s ease',
      }}
      onMouseEnter={e => { e.currentTarget.style.background = 'rgba(244,63,94,0.16)'; e.currentTarget.style.borderColor = 'rgba(244,63,94,0.4)' }}
      onMouseLeave={e => { e.currentTarget.style.background = 'rgba(244,63,94,0.07)'; e.currentTarget.style.borderColor = 'rgba(244,63,94,0.2)' }}>
        Remove
      </button>
    </div>
  )
}

function StepHeader({ num, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
      <div style={{
        width: 26, height: 26, borderRadius: 8, flexShrink: 0,
        background: 'rgba(0,229,255,0.08)', border: '1px solid rgba(0,229,255,0.25)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 11, fontWeight: 900, color: 'var(--accent)',
        fontFamily: "'Orbitron',sans-serif",
      }}>{num}</div>
      <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--accent)' }}>
        {label}
      </span>
      <div style={{ flex: 1, height: 1, background: 'rgba(0,229,255,0.07)' }} />
    </div>
  )
}

export default function Enroll() {
  const [file, setFile]   = useState(null)
  const [name, setName]   = useState('')
  const [enrolling, setEnrolling] = useState(false)
  const [enrollMsg, setEnrollMsg] = useState(null)
  const [gallery, setGallery] = useState([])
  const [probeFile, setProbeFile]   = useState(null)
  const [searching, setSearching]   = useState(false)
  const [searchResults, setSearchResults] = useState(null)
  const [searchError, setSearchError]    = useState('')

  async function loadGallery() {
    try { const res = await getEnrolled(); setGallery(res.identities) } catch (_) {}
  }

  useEffect(() => { loadGallery() }, [])

  async function handleEnroll() {
    if (!file || !name.trim()) return
    setEnrolling(true); setEnrollMsg(null)
    try {
      const res = await enrollFace(name.trim(), file)
      setEnrollMsg({ ok: true, text: `✓ "${res.enrolled}" enrolled — ${res.total} identit${res.total === 1 ? 'y' : 'ies'} in gallery` })
      setFile(null); setName('')
      loadGallery()
    } catch (e) {
      setEnrollMsg({ ok: false, text: e.message })
    } finally { setEnrolling(false) }
  }

  async function handleDelete(n) {
    try { await deleteEnrolled(n); loadGallery() } catch (_) {}
  }

  async function handleSearch() {
    if (!probeFile) return
    setSearching(true); setSearchError(''); setSearchResults(null)
    try { setSearchResults(await identifyEnrolled(probeFile, 5)) }
    catch (e) { setSearchError(e.message) }
    finally { setSearching(false) }
  }

  return (
    <div style={{ maxWidth: 1060, margin: '0 auto', padding: '48px 28px 60px' }}>
      {/* Header */}
      <div style={{ marginBottom: 40 }}>
        <div className="page-eyebrow">
          <span style={{
            display: 'inline-block', width: 5, height: 5, borderRadius: '50%',
            background: 'var(--accent)', animation: 'dot-pulse 2s ease-in-out infinite',
          }}/>
          Gallery Management
        </div>
        <h2 style={{
          fontSize: 40, fontWeight: 900, letterSpacing: '-0.03em',
          background: 'linear-gradient(135deg, var(--text-pri) 0%, var(--accent) 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          marginBottom: 8,
        }}>Enroll Faces</h2>
        <p className="section-sub" style={{ fontSize: 16 }}>
          Add identities to the biometric gallery · then probe the gallery for 1:N identification
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, alignItems: 'start' }}>

        {/* ── Left: Enroll ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <StepHeader num="01" label="Add Identity" />

          <DropZone file={file} onFile={setFile} />

          <input
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleEnroll()}
            placeholder="Full name or identity label…"
            style={{
              background: 'linear-gradient(145deg, rgba(22,34,62,0.94), rgba(14,22,46,0.97))',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 10, padding: '14px 16px', color: 'var(--text-pri)',
              fontSize: 14, outline: 'none', fontFamily: 'Inter,sans-serif',
              transition: 'border-color 0.2s, box-shadow 0.2s',
            }}
            onFocus={e => { e.target.style.borderColor = 'rgba(0,229,255,0.35)'; e.target.style.boxShadow = '0 0 20px rgba(0,229,255,0.06)' }}
            onBlur={e => { e.target.style.borderColor = 'rgba(255,255,255,0.08)'; e.target.style.boxShadow = 'none' }}
          />

          <button className="btn-primary" onClick={handleEnroll}
            disabled={enrolling || !file || !name.trim()}
            style={{ padding: '14px', fontSize: 12, letterSpacing: '0.1em' }}>
            {enrolling
              ? <><span className="spin" style={{ marginRight: 8 }}>◌</span>Enrolling…</>
              : '⊕  Enroll Identity'
            }
          </button>

          {enrollMsg && (
            <div style={{
              fontSize: 13, padding: '11px 14px', borderRadius: 9,
              color: enrollMsg.ok ? 'var(--success)' : 'var(--danger)',
              background: enrollMsg.ok ? 'rgba(16,185,129,0.06)' : 'rgba(244,63,94,0.06)',
              border: `1px solid ${enrollMsg.ok ? 'rgba(16,185,129,0.25)' : 'rgba(244,63,94,0.25)'}`,
            }}>{enrollMsg.text}</div>
          )}

          {/* Gallery */}
          <div style={{ marginTop: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              <div style={{ height: 1, width: 18, background: 'rgba(0,229,255,0.35)' }}/>
              <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--accent)' }}>
                Enrolled Gallery
              </span>
              <div style={{
                fontSize: 9, background: 'rgba(0,229,255,0.08)', border: '1px solid rgba(0,229,255,0.2)',
                borderRadius: 20, padding: '2px 9px', color: 'var(--accent)', fontWeight: 800,
              }}>{gallery.length}</div>
            </div>

            {gallery.length === 0 ? (
              <div style={{
                textAlign: 'center', padding: '28px 20px',
                border: '1px dashed rgba(255,255,255,0.06)', borderRadius: 12,
                color: 'var(--text-muted)', fontSize: 13,
              }}>No identities enrolled yet</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {gallery.map(n => <IdentityCard key={n} name={n} onDelete={handleDelete} />)}
              </div>
            )}
          </div>
        </div>

        {/* ── Right: Probe ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <StepHeader num="02" label="Probe the Gallery" />

          <DropZone file={probeFile} onFile={setProbeFile} compact />

          <button
            className={gallery.length > 0 ? 'btn-primary' : 'btn-ghost'}
            onClick={handleSearch}
            disabled={searching || !probeFile || gallery.length === 0}
            style={{ padding: '14px', fontSize: 12, letterSpacing: '0.1em' }}>
            {searching
              ? <><span className="spin" style={{ marginRight: 8 }}>◌</span>Searching…</>
              : gallery.length === 0
                ? 'Enroll identities first'
                : '⊙  Search Enrolled Gallery'
            }
          </button>

          {searchError && (
            <div style={{
              color: 'var(--danger)', fontSize: 13, padding: '11px 14px', borderRadius: 9,
              background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.22)',
            }}>{searchError}</div>
          )}

          {searchResults && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{
                fontSize: 11, color: 'var(--text-muted)', padding: '8px 14px',
                background: 'rgba(0,229,255,0.03)', border: '1px solid rgba(0,229,255,0.08)',
                borderRadius: 8,
              }}>
                Searched <b style={{ color: 'var(--accent)' }}>{searchResults.n_enrolled}</b> enrolled{' '}
                identit{searchResults.n_enrolled === 1 ? 'y' : 'ies'}
              </div>

              {searchResults.results.map((r, i) => {
                const isTop = i === 0
                const hue = [...r.name].reduce((h, c) => h + c.charCodeAt(0), 0) % 360
                const initials = r.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
                return (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px',
                    background: isTop
                      ? 'linear-gradient(135deg, rgba(0,229,255,0.05), rgba(0,229,255,0.02))'
                      : 'linear-gradient(135deg, rgba(22,34,62,0.88), rgba(14,22,46,0.94))',
                    border: `1px solid ${isTop ? 'rgba(0,229,255,0.22)' : 'rgba(255,255,255,0.06)'}`,
                    borderRadius: 12,
                    boxShadow: isTop ? '0 0 28px rgba(0,229,255,0.06)' : 'none',
                    transition: 'all 0.18s ease',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.transform = 'translateX(4px)' }}
                  onMouseLeave={e => { e.currentTarget.style.transform = '' }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                      background: isTop ? 'rgba(0,229,255,0.12)' : 'rgba(255,255,255,0.04)',
                      border: `1px solid ${isTop ? 'rgba(0,229,255,0.32)' : 'rgba(255,255,255,0.07)'}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 11, fontWeight: 900,
                      color: isTop ? 'var(--accent)' : 'var(--text-muted)',
                      fontFamily: "'Orbitron',sans-serif",
                    }}>{r.rank}</div>

                    <div style={{
                      width: 38, height: 38, borderRadius: 10, flexShrink: 0,
                      background: `hsl(${hue},55%,18%)`,
                      border: `1px solid hsl(${hue},55%,32%)`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 12, fontWeight: 800, color: `hsl(${hue},75%,68%)`,
                    }}>{initials || '?'}</div>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        fontSize: 13, fontWeight: isTop ? 700 : 500,
                        color: isTop ? 'var(--text-pri)' : 'var(--text-sec)',
                        marginBottom: 5,
                      }}>{r.name}</div>
                      <div style={{ height: 3, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
                        <div style={{
                          width: `${Math.max(0, Math.round(r.similarity * 100))}%`, height: '100%',
                          background: isTop ? 'linear-gradient(90deg, var(--accent), #a855f7)' : 'rgba(0,229,255,0.35)',
                          borderRadius: 2, transition: 'width 0.5s ease',
                        }}/>
                      </div>
                    </div>

                    <div style={{
                      fontSize: 15, fontWeight: 900, flexShrink: 0,
                      fontFamily: "'Orbitron',sans-serif",
                      color: isTop ? 'var(--accent)' : 'var(--text-muted)',
                      textShadow: isTop ? '0 0 14px rgba(0,229,255,0.6)' : 'none',
                    }}>{r.similarity.toFixed(4)}</div>
                  </div>
                )
              })}
            </div>
          )}

          {!searchResults && !searching && (
            <div style={{
              textAlign: 'center', padding: '52px 20px',
              border: '1px dashed rgba(255,255,255,0.06)', borderRadius: 14,
              color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14,
            }}>
              <div style={{
                width: 56, height: 56, borderRadius: 16,
                border: '1px solid rgba(0,229,255,0.1)',
                background: 'rgba(0,229,255,0.02)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 22, color: 'rgba(0,229,255,0.2)',
              }}>⊙</div>
              <div style={{ fontSize: 13, fontWeight: 500 }}>
                Upload a probe photo to identify against the enrolled gallery
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
