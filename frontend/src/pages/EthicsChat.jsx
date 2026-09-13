import { useState, useRef, useEffect } from 'react'
import { sendChat } from '../api'

const STARTERS = [
  { q: 'Summarise the race bias findings in plain English.', icon: '⚖', color: 'rgba(0,229,255,' },
  { q: 'Is this system deployable in the EU under the AI Act?', icon: '▤', color: 'rgba(139,92,246,' },
  { q: 'Why is the age FMRD so much worse than race FMRD?', icon: '◉', color: 'rgba(245,158,11,' },
  { q: 'What are the top 3 mitigations before deployment?', icon: '◈', color: 'rgba(16,185,129,' },
]

function Message({ role, content }) {
  const isUser = role === 'user'
  return (
    <div style={{
      display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 20, gap: 12, alignItems: 'flex-end',
    }}>
      {!isUser && (
        <div style={{
          width: 38, height: 38, borderRadius: 12, flexShrink: 0,
          background: 'linear-gradient(135deg, rgba(0,229,255,0.18), rgba(139,92,246,0.18))',
          border: '1px solid rgba(0,229,255,0.25)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 16, boxShadow: '0 0 24px rgba(0,229,255,0.15)',
        }}>⚖</div>
      )}
      <div style={{
        maxWidth: '76%', padding: '14px 18px',
        borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
        background: isUser
          ? 'linear-gradient(135deg, rgba(0,229,255,0.08), rgba(139,92,246,0.05))'
          : 'linear-gradient(145deg, rgba(22,34,62,0.98), rgba(16,25,50,0.99))',
        border: `1px solid ${isUser ? 'rgba(0,229,255,0.2)' : 'rgba(255,255,255,0.07)'}`,
        boxShadow: isUser ? '0 0 24px rgba(0,229,255,0.05)' : '0 4px 20px rgba(0,0,0,0.4)',
        fontSize: 14, lineHeight: 1.75, color: 'var(--text-pri)',
        whiteSpace: 'pre-wrap', wordBreak: 'break-word',
      }}>
        {content}
      </div>
      {isUser && (
        <div style={{
          width: 38, height: 38, borderRadius: 12, flexShrink: 0,
          background: 'rgba(0,229,255,0.07)',
          border: '1px solid rgba(0,229,255,0.18)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 14, color: 'var(--accent)',
        }}>◈</div>
      )}
    </div>
  )
}

export default function EthicsChat() {
  const [history, setHistory] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, loading])

  async function send(msg) {
    const text = (msg || input).trim()
    if (!text || loading) return
    setInput('')
    const newHistory = [...history, { role: 'user', content: text }]
    setHistory(newHistory)
    setLoading(true)
    try {
      const res = await sendChat(text, history)
      setHistory([...newHistory, { role: 'assistant', content: res.reply }])
    } catch (e) {
      setHistory([...newHistory, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally { setLoading(false) }
  }

  return (
    <div style={{
      maxWidth: 900, margin: '0 auto', padding: '20px 28px 20px',
      display: 'flex', flexDirection: 'column',
      height: 'calc(100vh - 72px)',
    }}>
      {/* Header */}
      <div style={{ marginBottom: 14, flexShrink: 0 }}>
        <div className="page-eyebrow">
          <span style={{
            display: 'inline-block', width: 5, height: 5, borderRadius: '50%',
            background: 'var(--accent)', animation: 'dot-pulse 2s ease-in-out infinite',
          }}/>
          Claude Sonnet · Live
        </div>
        <h2 style={{
          fontSize: 30, fontWeight: 900, letterSpacing: '-0.03em',
          background: 'linear-gradient(135deg, var(--text-pri) 0%, #a855f7 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          marginBottom: 4,
        }}>Ethics Officer</h2>
        <p className="section-sub" style={{ fontSize: 13 }}>
          Ask about bias findings, EU AI Act compliance, or mitigation strategies
        </p>
      </div>

      {/* Starter prompts */}
      {history.length === 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 10, marginBottom: 12, flexShrink: 0 }}>
          {STARTERS.map(s => (
            <button key={s.q} onClick={() => send(s.q)} style={{
              background: 'linear-gradient(145deg, rgba(22,34,62,0.92), rgba(14,22,46,0.96))',
              border: '1px solid rgba(255,255,255,0.07)',
              borderRadius: 14, padding: '16px 18px',
              color: 'var(--text-sec)', fontSize: 13, cursor: 'pointer',
              transition: 'all 0.22s ease', fontFamily: 'Inter,sans-serif',
              textAlign: 'left', lineHeight: 1.55,
              display: 'flex', gap: 12, alignItems: 'flex-start',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = 'rgba(0,229,255,0.2)'
              e.currentTarget.style.color = 'var(--text-pri)'
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(0,0,0,0.4)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'
              e.currentTarget.style.color = 'var(--text-sec)'
              e.currentTarget.style.transform = ''
              e.currentTarget.style.boxShadow = ''
            }}>
              <span style={{
                fontSize: 18, flexShrink: 0, width: 36, height: 36,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                borderRadius: 10,
                background: `${s.color}0.08)`,
                border: `1px solid ${s.color}0.18)`,
              }}>{s.icon}</span>
              <span style={{ paddingTop: 6 }}>{s.q}</span>
            </button>
          ))}
        </div>
      )}

      {/* Message area */}
      <div style={{
        flex: 1, overflowY: 'auto', padding: '20px',
        background: 'linear-gradient(145deg, rgba(14,24,50,0.7), rgba(12,20,42,0.65))',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 18, marginBottom: 12, minHeight: 0,
      }}>
        {history.length === 0 && (
          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            height: '100%', gap: 18, color: 'var(--text-muted)',
          }}>
            <div style={{
              width: 80, height: 80, borderRadius: 24,
              background: 'linear-gradient(135deg, rgba(0,229,255,0.07), rgba(139,92,246,0.07))',
              border: '1px solid rgba(0,229,255,0.12)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 36, animation: 'float 6s ease-in-out infinite',
              boxShadow: '0 0 40px rgba(139,92,246,0.1)',
            }}>⚖</div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-sec)', marginBottom: 6 }}>
                Ask the Ethics Officer anything
              </div>
              <div style={{ fontSize: 13 }}>
                Powered by Claude Sonnet with full ETHOS audit context
              </div>
            </div>
          </div>
        )}
        {history.map((m, i) => <Message key={i} {...m} />)}
        {loading && (
          <div style={{ display: 'flex', gap: 12, marginBottom: 12, alignItems: 'flex-end' }}>
            <div style={{
              width: 38, height: 38, borderRadius: 12, flexShrink: 0,
              background: 'linear-gradient(135deg, rgba(0,229,255,0.18), rgba(139,92,246,0.18))',
              border: '1px solid rgba(0,229,255,0.25)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16,
            }}>⚖</div>
            <div style={{
              padding: '14px 20px', borderRadius: '4px 16px 16px 16px',
              background: 'linear-gradient(145deg, rgba(22,34,62,0.98), rgba(16,25,50,0.99))',
              border: '1px solid rgba(255,255,255,0.07)',
              display: 'flex', gap: 6, alignItems: 'center',
            }}>
              {[0, 1, 2].map(i => (
                <span key={i} style={{
                  width: 7, height: 7, borderRadius: '50%', background: 'var(--accent)',
                  animation: 'dot-pulse 1.2s ease-in-out infinite',
                  animationDelay: `${i * 0.22}s`, display: 'inline-block',
                }}/>
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef}/>
      </div>

      {/* Input row */}
      <div style={{ display: 'flex', gap: 12, flexShrink: 0 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), send())}
          placeholder="Ask about bias, compliance, or mitigation…"
          style={{
            flex: 1,
            background: 'linear-gradient(145deg, rgba(22,34,62,0.96), rgba(14,22,46,0.98))',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 12, padding: '15px 18px', color: 'var(--text-pri)',
            fontSize: 14, outline: 'none', fontFamily: 'Inter,sans-serif',
            transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          }}
          onFocus={e => {
            e.target.style.borderColor = 'rgba(0,229,255,0.35)'
            e.target.style.boxShadow = '0 0 24px rgba(0,229,255,0.06)'
          }}
          onBlur={e => {
            e.target.style.borderColor = 'rgba(255,255,255,0.08)'
            e.target.style.boxShadow = 'none'
          }}
        />
        <button
          className="btn-primary"
          onClick={() => send()}
          disabled={loading || !input.trim()}
          style={{ padding: '14px 28px', flexShrink: 0 }}
        >
          Send →
        </button>
      </div>
    </div>
  )
}
