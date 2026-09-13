const PAGES = [
  { id: 'overview',  label: 'Overview',   icon: '◈', color: '#00e5ff' },
  { id: 'verify',    label: 'Verify',     icon: '⟺', color: '#00e5ff' },
  { id: 'identify',  label: 'Identify',   icon: '⊕', color: '#a78bfa' },
  { id: 'enroll',    label: 'Enroll',     icon: '⊞', color: '#34d399' },
  { id: 'fairness',  label: 'Fairness',   icon: '⚖', color: '#f87171' },
  { id: 'metrics',   label: 'Metrics',    icon: '◉', color: '#fbbf24' },
  { id: 'chat',      label: 'Ethics AI',  icon: '◊', color: '#c084fc' },
  { id: 'pad',       label: 'Live PAD',   icon: '⊙', color: '#f43f5e' },
  { id: 'report',    label: 'Report',     icon: '▤', color: '#10b981' },
]

export default function Nav({ current, onNav }) {
  const activePage = PAGES.find(p => p.id === current) || PAGES[0]

  return (
    <>
      <style>{`
        @keyframes nav-shimmer {
          0%,100% { background-position: 0% 50%; }
          50%      { background-position: 100% 50%; }
        }
        .nav-btn {
          background: none;
          border: none;
          padding: 0 4px;
          cursor: pointer;
          height: 100%;
          display: flex;
          align-items: center;
          flex-shrink: 0;
        }
        .nav-chip {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 7px 13px;
          border-radius: 10px;
          font-size: 12.5px;
          font-weight: 400;
          font-family: Inter, sans-serif;
          letter-spacing: 0.01em;
          white-space: nowrap;
          border: 1px solid transparent;
          transition: all 0.2s cubic-bezier(0.4,0,0.2,1);
          color: rgba(210,228,255,0.65);
          position: relative;
        }
        .nav-chip:hover {
          color: rgba(240,250,255,0.92);
          background: rgba(255,255,255,0.07);
          border-color: rgba(255,255,255,0.14);
          transform: translateY(-1px);
        }
        .nav-chip.active {
          font-weight: 700;
          color: #fff;
          transform: translateY(-1px);
        }
        .nav-chip .icon {
          font-size: 13px;
          opacity: 0.45;
          transition: all 0.2s ease;
          line-height: 1;
        }
        .nav-chip:hover .icon {
          opacity: 0.75;
        }
        .nav-chip.active .icon {
          opacity: 1;
        }
      `}</style>

      <header style={{
        position: 'sticky', top: 0, zIndex: 200,
        display: 'flex', alignItems: 'center',
        padding: '0 24px', height: 80,
        background: 'linear-gradient(180deg, rgba(12,20,42,0.99) 0%, rgba(10,17,36,0.99) 100%)',
        backdropFilter: 'blur(48px) saturate(180%)',
        WebkitBackdropFilter: 'blur(48px) saturate(180%)',
        borderBottom: '1px solid rgba(255,255,255,0.08)',
        boxShadow: '0 24px 60px rgba(0,0,0,0.6)',
        position: 'relative',
        overflow: 'hidden',
      }}>

        {/* Animated shimmer bar along the bottom edge */}
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: 2,
          background: 'linear-gradient(90deg, #00e5ff, #8b5cf6, #f0abfc, #f43f5e, #fbbf24, #10b981, #00e5ff)',
          backgroundSize: '300% 100%',
          animation: 'nav-shimmer 6s ease infinite',
          opacity: 0.7,
        }}/>

        {/* Very faint top highlight */}
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: 1,
          background: 'linear-gradient(90deg, transparent 0%, rgba(0,229,255,0.3) 30%, rgba(139,92,246,0.3) 70%, transparent 100%)',
        }}/>

        {/* ── Brand ── */}
        <div
          onClick={() => onNav('overview')}
          style={{ display: 'flex', alignItems: 'center', gap: 13, cursor: 'pointer', flexShrink: 0, marginRight: 28 }}
        >
          {/* Spinning conic ring */}
          <div style={{ position: 'relative', width: 42, height: 42, flexShrink: 0 }}>
            <div style={{
              position: 'absolute', inset: 0, borderRadius: '50%',
              background: 'conic-gradient(from 0deg, #00e5ff, #8b5cf6, #f0abfc, #f43f5e, #fbbf24, #00e5ff)',
              animation: 'spin 4s linear infinite',
            }}/>
            <div style={{
              position: 'absolute', inset: 3, borderRadius: '50%',
              background: '#0b1528',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 15, color: '#00e5ff',
              textShadow: '0 0 16px rgba(0,229,255,1)',
            }}>◈</div>
          </div>

          <div style={{ lineHeight: 1 }}>
            <div style={{
              fontSize: 20, fontWeight: 900, letterSpacing: '0.26em',
              fontFamily: "'Orbitron', sans-serif",
              background: 'linear-gradient(135deg, #00e5ff 0%, #c084fc 60%, #f0abfc 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
              lineHeight: 1, marginBottom: 5,
            }}>ETHOS</div>
            <div style={{
              fontSize: 8.5, letterSpacing: '0.16em', fontWeight: 600,
              color: 'rgba(170,205,240,0.5)', textTransform: 'uppercase',
            }}>Fairness Auditor · v1.0</div>
          </div>
        </div>

        {/* ── Separator ── */}
        <div style={{ width: 1, height: 36, background: 'rgba(255,255,255,0.1)', marginRight: 24, flexShrink: 0, borderRadius: 1 }}/>

        {/* ── Nav items ── */}
        <nav style={{
          display: 'flex', alignItems: 'center', gap: 1,
          flex: 1, height: '100%',
          overflowX: 'auto', scrollbarWidth: 'none', msOverflowStyle: 'none',
        }}>
          {PAGES.map(p => {
            const active = current === p.id
            const c = p.color
            return (
              <button key={p.id} className="nav-btn" onClick={() => onNav(p.id)}>
                <div
                  className={`nav-chip${active ? ' active' : ''}`}
                  style={active ? {
                    background: `linear-gradient(135deg, ${c}28, ${c}12)`,
                    borderColor: `${c}88`,
                    boxShadow: `0 0 32px ${c}44, 0 0 64px ${c}18, inset 0 0 20px ${c}12`,
                    color: c,
                    textShadow: `0 0 20px ${c}cc`,
                  } : {}}
                >
                  <span
                    className="icon"
                    style={active ? { filter: `drop-shadow(0 0 8px ${c})`, color: c } : {}}
                  >{p.icon}</span>
                  {p.label}
                  {/* Active dot indicator below */}
                  {active && (
                    <span style={{
                      position: 'absolute', bottom: -14, left: '50%', transform: 'translateX(-50%)',
                      width: 4, height: 4, borderRadius: '50%',
                      background: c, boxShadow: `0 0 8px ${c}`,
                      animation: 'dot-pulse 2s ease-in-out infinite',
                    }}/>
                  )}
                </div>
              </button>
            )
          })}
        </nav>

        {/* ── Right panel ── */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0, marginLeft: 10 }}>

          {/* Live badge */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '5px 11px', borderRadius: 9,
            background: 'rgba(16,185,129,0.1)',
            border: '1px solid rgba(16,185,129,0.35)',
            fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
            color: '#10b981', textTransform: 'uppercase',
            boxShadow: '0 0 16px rgba(16,185,129,0.1)',
          }}>
            <span style={{
              width: 7, height: 7, borderRadius: '50%', background: '#10b981',
              boxShadow: '0 0 10px #10b981', display: 'inline-block',
              animation: 'dot-pulse 1.8s ease-in-out infinite',
            }}/>
            Live
          </div>

          {/* EU AI Act */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '5px 11px', borderRadius: 9,
            background: 'rgba(0,229,255,0.08)',
            border: '1px solid rgba(0,229,255,0.35)',
            fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
            color: '#00e5ff', textTransform: 'uppercase',
            animation: 'badge-glow 3s ease-in-out infinite alternate',
            boxShadow: '0 0 20px rgba(0,229,255,0.12)',
          }}>
            <span style={{
              width: 6, height: 6, borderRadius: '50%', background: '#00e5ff',
              boxShadow: '0 0 8px #00e5ff', display: 'inline-block',
              animation: 'dot-pulse 2.5s ease-in-out 0.4s infinite',
            }}/>
            EU AI Act
          </div>
        </div>
      </header>
    </>
  )
}
