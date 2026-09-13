import { useState, useEffect } from 'react'

const ITEMS = [
  { label: 'ArcFace buffalo_l',  dot: 'var(--success)', delay: 0 },
  { label: 'RetinaFace',         dot: 'var(--success)', delay: 0.3 },
  { label: 'MiniFASNetV2',       dot: 'var(--success)', delay: 0.6 },
  { label: 'FairFace 86k',       dot: 'var(--success)', delay: 0.9 },
  { label: 'Claude Sonnet',      dot: 'var(--success)', delay: 1.2 },
  { label: 'CoreML · M4',        dot: 'var(--accent)',  delay: 0 },
  { label: 'EU AI Act v1.0',     dot: 'var(--accent)',  delay: 0 },
]

function EKG() {
  return (
    <div style={{
      position: 'relative', flexShrink: 0,
      display: 'flex', alignItems: 'center', gap: 10,
      background: 'rgba(0,229,255,0.04)',
      border: '1px solid rgba(0,229,255,0.14)',
      borderRadius: 10,
      padding: '5px 14px 5px 12px',
    }}>
      <style>{`
        @keyframes ekg-sweep {
          0%,5%   { stroke-dashoffset: 220; opacity: 0; }
          15%     { opacity: 1; }
          62%     { stroke-dashoffset: 0; opacity: 1; }
          78%     { stroke-dashoffset: -220; opacity: 0.2; }
          85%,100%{ stroke-dashoffset: -220; opacity: 0; }
        }
        @keyframes ekg-panel-glow {
          0%,100% { box-shadow: 0 0 8px rgba(0,229,255,0.08), inset 0 0 12px rgba(0,229,255,0.04); }
          50%     { box-shadow: 0 0 20px rgba(0,229,255,0.18), inset 0 0 20px rgba(0,229,255,0.08); }
        }
        .ekg-panel { animation: ekg-panel-glow 2.8s ease-in-out infinite; }
      `}</style>

      {/* Label */}
      <div style={{
        fontSize: 7.5, fontWeight: 800, letterSpacing: '0.18em',
        color: 'rgba(0,229,255,0.55)', textTransform: 'uppercase',
        lineHeight: 1, flexShrink: 0,
        fontFamily: "'Orbitron', monospace",
      }}>
        BIO<br/>
        <span style={{ color: 'rgba(0,229,255,0.35)' }}>SYS</span>
      </div>

      <svg width="148" height="36" viewBox="0 0 148 36" fill="none" style={{ overflow: 'visible', display: 'block', flexShrink: 0 }}>
        {/* Background shimmer area */}
        <rect x="0" y="12" width="148" height="12" rx="6" fill="rgba(0,229,255,0.03)"/>
        {/* Baseline */}
        <line x1="0" y1="18" x2="148" y2="18" stroke="rgba(0,229,255,0.1)" strokeWidth="0.8" strokeDasharray="3 4"/>
        {/* Main EKG path — big dramatic spikes */}
        <path
          d="M 0,18 L 22,18 L 28,3 L 34,33 L 40,18 L 56,18 L 63,10 L 72,26 L 79,18 L 148,18"
          stroke="#00e5ff"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          strokeDasharray="220"
          strokeDashoffset="220"
          style={{
            animation: 'ekg-sweep 3s ease-in-out infinite',
            filter: 'drop-shadow(0 0 3px rgba(0,229,255,1)) drop-shadow(0 0 8px rgba(0,229,255,0.8)) drop-shadow(0 0 18px rgba(0,229,255,0.5))',
          }}
        />
        {/* Glow duplicate — blurred layer for bloom */}
        <path
          d="M 0,18 L 22,18 L 28,3 L 34,33 L 40,18 L 56,18 L 63,10 L 72,26 L 79,18 L 148,18"
          stroke="rgba(0,229,255,0.35)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          strokeDasharray="220"
          strokeDashoffset="220"
          style={{
            animation: 'ekg-sweep 3s ease-in-out infinite',
            filter: 'blur(4px)',
          }}
        />
      </svg>
    </div>
  )
}

export default function StatusBar() {
  const [time, setTime] = useState(() => new Date())

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  const pad = n => String(n).padStart(2, '0')
  const clock = `${pad(time.getHours())}:${pad(time.getMinutes())}:${pad(time.getSeconds())}`

  return (
    <footer style={{
      position: 'sticky', bottom: 0, zIndex: 100,
      height: 46,
      background: 'linear-gradient(180deg, rgba(8,14,30,0.99) 0%, rgba(5,9,20,1) 100%)',
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
      borderTop: '1px solid rgba(0,229,255,0.12)',
      display: 'flex', alignItems: 'center',
      padding: '0 20px',
      overflow: 'hidden',
      boxShadow: '0 -14px 50px rgba(0,0,0,0.55), 0 -1px 0 rgba(0,229,255,0.06)',
    }}>

      {/* Brand */}
      <div style={{
        fontSize: 9.5, fontWeight: 900, letterSpacing: '0.3em',
        fontFamily: "'Orbitron', sans-serif",
        background: 'linear-gradient(90deg, #00e5ff, #a855f7)',
        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        marginRight: 16, flexShrink: 0,
        filter: 'drop-shadow(0 0 8px rgba(0,229,255,0.4))',
      }}>ETHOS</div>

      <div style={{ width: 1, height: 22, background: 'rgba(0,229,255,0.12)', marginRight: 14, flexShrink: 0 }}/>

      {/* EKG — prominent framed panel */}
      <EKG />

      <div style={{ width: 1, height: 22, background: 'rgba(0,229,255,0.12)', marginLeft: 14, marginRight: 14, flexShrink: 0 }}/>

      {/* All systems */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6,
        fontSize: 8.5, fontWeight: 800, letterSpacing: '0.12em',
        color: 'var(--success)', textTransform: 'uppercase',
        marginRight: 14, flexShrink: 0,
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: '50%',
          background: 'var(--success)',
          boxShadow: '0 0 10px var(--success)',
          animation: 'dot-pulse 2s ease-in-out infinite',
          display: 'inline-block',
        }}/>
        All Systems
      </div>

      <div style={{ width: 1, height: 22, background: 'rgba(255,255,255,0.05)', marginRight: 14, flexShrink: 0 }}/>

      {/* Model pills */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 14, flex: 1,
        overflow: 'hidden',
      }}>
        {ITEMS.map(({ label, dot, delay }) => (
          <div key={label} style={{
            display: 'flex', alignItems: 'center', gap: 5,
            fontSize: 8.5, fontWeight: 500, letterSpacing: '0.03em',
            color: 'rgba(130,165,200,0.6)', whiteSpace: 'nowrap', flexShrink: 0,
          }}>
            <span style={{
              width: 4, height: 4, borderRadius: '50%',
              background: dot, flexShrink: 0,
              boxShadow: `0 0 6px ${dot}`,
              animation: `dot-pulse 2.4s ease-in-out ${delay}s infinite`,
              display: 'inline-block',
            }}/>
            {label}
          </div>
        ))}
      </div>

      <div style={{ width: 1, height: 22, background: 'rgba(255,255,255,0.05)', marginLeft: 10, marginRight: 14, flexShrink: 0 }}/>

      {/* Right: thesis + clock */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexShrink: 0 }}>
        <div style={{
          fontSize: 8, fontWeight: 500, letterSpacing: '0.07em',
          color: 'rgba(140,175,210,0.4)',
        }}>
          Master's Thesis · UPEC 2026
        </div>
        <div style={{
          fontSize: 10.5, fontWeight: 700, letterSpacing: '0.14em',
          color: 'var(--accent)', fontFamily: 'monospace',
          textShadow: '0 0 16px rgba(0,229,255,0.7)',
          background: 'rgba(0,229,255,0.06)',
          border: '1px solid rgba(0,229,255,0.18)',
          borderRadius: 6, padding: '3px 10px',
        }}>
          {clock}
        </div>
      </div>
    </footer>
  )
}
