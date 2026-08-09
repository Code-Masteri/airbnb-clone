'use client'

import { useState, useRef, useEffect, useCallback } from 'react'

// ─── Icons (inline SVG components) ────────────────────────────────────────────
const IconSearch = () => <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.5"/><path d="M14 14l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
const IconHome = () => <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M3 9.5L10 3l7 6.5V17a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/></svg>
const IconFolder = () => <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M2 6a2 2 0 012-2h3.586a1 1 0 01.707.293L9.414 5.4A1 1 0 0010.121 5.7H16a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" stroke="currentColor" strokeWidth="1.5"/></svg>
const IconClock = () => <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/><path d="M10 6v4l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
const IconPlus = () => <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M10 4v12M4 10h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
const IconSettings = () => <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="2.5" stroke="currentColor" strokeWidth="1.5"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.22 4.22l1.42 1.42M14.36 14.36l1.42 1.42M15.78 4.22l-1.42 1.42M5.64 14.36l-1.42 1.42" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
const IconRefresh = () => <svg width="13" height="13" viewBox="0 0 20 20" fill="none"><path d="M4 10a6 6 0 1011.66-2M4 10V6M4 10H8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
const IconAttach = () => <svg width="14" height="14" viewBox="0 0 20 20" fill="none"><path d="M16.5 10.5l-7.5 7.5a5 5 0 01-7.07-7.07l8-8a3 3 0 014.24 4.24l-8 8a1 1 0 01-1.42-1.42l7.5-7.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
const IconImage = () => <svg width="14" height="14" viewBox="0 0 20 20" fill="none"><rect x="2" y="4" width="16" height="13" rx="2" stroke="currentColor" strokeWidth="1.5"/><circle cx="7.5" cy="9.5" r="1.5" stroke="currentColor" strokeWidth="1.3"/><path d="M2 14l4-4 4 4 3-3 5 5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg>
const IconGlobe = () => <svg width="14" height="14" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.3"/><path d="M10 3C8 5.5 7 7.5 7 10s1 4.5 3 7M10 3c2 2.5 3 4.5 3 7s-1 4.5-3 7M3 10h14" stroke="currentColor" strokeWidth="1.3"/></svg>
const IconChevron = () => <svg width="10" height="10" viewBox="0 0 20 20" fill="none"><path d="M6 8l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
const IconArrow = () => <svg width="14" height="14" viewBox="0 0 20 20" fill="none"><path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>

// ─── Prompt cards (matching the image exactly) ─────────────────────────────
const PROMPT_CARDS = [
  { text: 'Roast my startup idea and tell me what will kill it', icon: <IconHome /> },
  { text: 'Tear apart my plan before I waste months on it', icon: <IconFolder /> },
  { text: 'Show me where I\'ll be in 6 months if I keep this habit', icon: <IconClock /> },
  { text: 'Give me the brutal truth about my career move', icon: <IconSettings /> },
]

// ─── Response formatter ────────────────────────────────────────────────────
function formatResponse(text: string) {
  const SECTIONS = ['THE VERDICT', "WHAT'S BROKEN", 'IF YOU DO NOTHING', 'THE FIX', 'THE ONE THING']
  const lines = text.split('\n')
  const out: React.ReactNode[] = []

  lines.forEach((line, i) => {
    const trimmed = line.trim()
    if (!trimmed) { out.push(<br key={i} />); return }

    const isSection = SECTIONS.some(s => trimmed === s || trimmed.startsWith(s + ':'))
    if (isSection) {
      const label = SECTIONS.find(s => trimmed.startsWith(s)) || trimmed
      out.push(<span key={i} className="grim-label">{label.replace(':', '')}</span>)
      const rest = trimmed.slice(label.length).replace(/^:\s*/, '')
      if (rest) out.push(<p key={i + 'r'} style={{ marginBottom: 4 }}>{rest}</p>)
      return
    }

    if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
      out.push(
        <li key={i} style={{ marginBottom: 3, listStyleType: 'disc', marginLeft: 16 }}>
          {trimmed.slice(2)}
        </li>
      )
      return
    }

    if (trimmed.startsWith('*') && trimmed.endsWith('*') && trimmed.length > 2) {
      out.push(
        <p key={i} style={{ color: 'var(--text-muted)', fontStyle: 'italic', marginTop: 12, fontSize: 13 }}>
          {trimmed.slice(1, -1)}
        </p>
      )
      return
    }

    out.push(<p key={i} style={{ marginBottom: 4 }}>{trimmed}</p>)
  })

  return out
}

// ─── Main page ─────────────────────────────────────────────────────────────
export default function Home() {
  const [input, setInput] = useState('')
  const [response, setResponse] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [done, setDone] = useState(false)
  const [dark, setDark] = useState(false)
  const [activeNav, setActiveNav] = useState(1)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  useEffect(() => {
    if (streaming) bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [response, streaming])

  const ask = useCallback(async (msg: string) => {
    const message = msg.trim()
    if (!message || streaming) return
    setResponse('')
    setDone(false)
    setStreaming(true)

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      })
      if (!res.body) throw new Error()
      const reader = res.body.getReader()
      const dec = new TextDecoder()
      while (true) {
        const { done: d, value } = await reader.read()
        if (d) break
        setResponse(p => p + dec.decode(value))
      }
    } catch {
      setResponse("THE VERDICT\n\nCan't reach Grim.\n\nWHAT'S BROKEN\n- API server not running\n- Run: python server.py in your grimai folder\n- Check http://localhost:8000/health")
    } finally {
      setStreaming(false)
      setDone(true)
    }
  }, [streaming])

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.metaKey) ask(input)
  }

  const pickCard = (text: string) => {
    setInput(text)
    textareaRef.current?.focus()
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)' }}>

      {/* ── Sidebar ── */}
      <aside style={{
        width: 52,
        background: 'var(--sidebar)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '14px 0',
        gap: 4,
        flexShrink: 0,
      }}>
        {/* Logo */}
        <div style={{
          width: 32, height: 32,
          background: 'var(--text)',
          borderRadius: 10,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          marginBottom: 12, cursor: 'pointer', flexShrink: 0,
        }}>
          <svg width="13" height="13" viewBox="0 0 20 20" fill="none">
            <path d="M4 4l6 6m0 0l6-6M10 10l6 6m-6-6L4 16" stroke="var(--bg)" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </div>

        {/* Nav */}
        <SidebarBtn active={activeNav === 0} onClick={() => setActiveNav(0)}><IconPlus /></SidebarBtn>
        <SidebarBtn active={activeNav === 1} onClick={() => setActiveNav(1)}><IconSearch /></SidebarBtn>
        <SidebarBtn active={activeNav === 2} onClick={() => setActiveNav(2)}><IconHome /></SidebarBtn>
        <SidebarBtn active={activeNav === 3} onClick={() => setActiveNav(3)}><IconFolder /></SidebarBtn>
        <SidebarBtn active={activeNav === 4} onClick={() => setActiveNav(4)}><IconClock /></SidebarBtn>

        {/* Bottom */}
        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
          <SidebarBtn active={false} onClick={() => setDark(d => !d)}>
            {dark
              ? <svg width="15" height="15" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.41 1.41M13.66 13.66l1.41 1.41M15.07 4.93l-1.41 1.41M6.34 13.66l-1.41 1.41" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
              : <svg width="15" height="15" viewBox="0 0 20 20" fill="none"><path d="M17 12A7 7 0 118 3a5 5 0 009 9z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/></svg>
            }
          </SidebarBtn>
          <SidebarBtn active={false} onClick={() => {}}><IconSettings /></SidebarBtn>
          {/* Avatar */}
          <div style={{
            width: 28, height: 28, borderRadius: '50%',
            background: 'linear-gradient(135deg, #c9a96e, #8B6914)',
            cursor: 'pointer', marginTop: 4,
          }} />
        </div>
      </aside>

      {/* ── Main ── */}
      <main style={{
        flex: 1, overflowY: 'auto',
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        padding: '0 24px',
      }}>
        <div style={{ width: '100%', maxWidth: 680, paddingTop: 80, paddingBottom: 60 }}>

          {/* Greeting — matches image font weight + color split */}
          <h1 style={{
            fontSize: 34,
            fontWeight: 600,
            lineHeight: 1.2,
            letterSpacing: '-0.5px',
            marginBottom: 8,
            color: 'var(--text)',
          }}>
            Hi there,{' '}
            <span style={{ color: '#7B61FF' }}>Faza</span>
            <br />
            What would{' '}
            <span style={{
              background: 'linear-gradient(90deg, #7B61FF, #C084FC)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              Grim tear apart?
            </span>
          </h1>

          <p style={{ color: 'var(--text-muted)', fontSize: 13, fontWeight: 300, marginBottom: 28 }}>
            Use one of the prompts below or write your own to begin
          </p>

          {/* Prompt cards — 4 column grid matching image */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: 10,
            marginBottom: 10,
          }}>
            {PROMPT_CARDS.map((card, i) => (
              <button
                key={i}
                onClick={() => pickCard(card.text)}
                style={{
                  background: 'var(--surface-card)',
                  border: '1px solid var(--border)',
                  borderRadius: 12,
                  padding: '14px 14px 12px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  minHeight: 108,
                  transition: 'border-color 0.15s',
                  color: 'var(--text)',
                }}
                onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--border-hover)')}
                onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
              >
                <span style={{ fontSize: 12.5, lineHeight: 1.5, fontWeight: 400, color: 'var(--text)' }}>
                  {card.text}
                </span>
                <span style={{ color: 'var(--text-faint)', marginTop: 12 }}>
                  {card.icon}
                </span>
              </button>
            ))}
          </div>

          {/* Refresh prompts */}
          <button
            onClick={() => {}}
            style={{
              display: 'flex', alignItems: 'center', gap: 5,
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--text-muted)', fontSize: 12, fontWeight: 400,
              marginBottom: 24, padding: '4px 0',
            }}
          >
            <IconRefresh /> Refresh Prompts
          </button>

          {/* Input box — matches image exactly */}
          <div style={{
            background: 'var(--surface-card)',
            border: '1px solid var(--border)',
            borderRadius: 14,
            padding: '14px 16px',
            transition: 'border-color 0.15s',
          }}>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask whatever you want...."
              rows={2}
              style={{
                width: '100%', background: 'none', border: 'none', outline: 'none',
                resize: 'none', fontSize: 14, color: 'var(--text)',
                fontFamily: 'inherit', lineHeight: 1.6, fontWeight: 300,
              }}
            />
            {/* Toolbar row */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                {/* All Web pill */}
                <button style={{
                  display: 'flex', alignItems: 'center', gap: 5,
                  border: '1px solid var(--border)',
                  borderRadius: 8, padding: '5px 10px',
                  background: 'none', cursor: 'pointer',
                  color: 'var(--text-muted)', fontSize: 12, fontFamily: 'inherit',
                }}>
                  <IconGlobe /> All Web <IconChevron />
                </button>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                {/* Add Attachment */}
                <button style={{
                  display: 'flex', alignItems: 'center', gap: 5,
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--text-muted)', fontSize: 12, fontFamily: 'inherit',
                }}>
                  <IconAttach /> Add Attachment
                </button>
                {/* Use Image */}
                <button style={{
                  display: 'flex', alignItems: 'center', gap: 5,
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--text-muted)', fontSize: 12, fontFamily: 'inherit',
                }}>
                  <IconImage /> Use Image
                </button>
                {/* Char count + Send */}
                <span style={{ fontSize: 11, color: 'var(--text-faint)' }}>
                  {input.length}/1000
                </span>
                <button
                  onClick={() => ask(input)}
                  disabled={streaming || !input.trim()}
                  style={{
                    width: 32, height: 32, borderRadius: 9,
                    background: streaming || !input.trim() ? '#9B8FF0' : 'var(--send)',
                    border: 'none', cursor: streaming || !input.trim() ? 'not-allowed' : 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: '#fff', transition: 'background 0.15s',
                  }}
                >
                  {streaming
                    ? <svg width="13" height="13" viewBox="0 0 20 20" fill="none" style={{ animation: 'spin 1s linear infinite' }}><path d="M10 3a7 7 0 100 14A7 7 0 0010 3z" stroke="white" strokeWidth="2" strokeDasharray="30" strokeDashoffset="10"/></svg>
                    : <IconArrow />
                  }
                </button>
              </div>
            </div>
          </div>

          {/* Response box */}
          {(streaming || done) && (
            <div style={{
              marginTop: 20,
              background: 'var(--surface-card)',
              border: '1px solid var(--border)',
              borderRadius: 14,
              padding: '20px 20px',
            }}>
              <p style={{
                fontSize: 10, fontWeight: 500, letterSpacing: '0.1em',
                textTransform: 'uppercase', color: 'var(--text-faint)', marginBottom: 12,
              }}>
                Grim
              </p>
              <div className="grim-response">
                {formatResponse(response)}
                {streaming && <span className="cursor" />}
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </main>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        textarea::placeholder { color: var(--text-faint); font-weight: 300; }
        button { font-family: inherit; }
      `}</style>
    </div>
  )
}

// ─── Sidebar button ────────────────────────────────────────────────────────
function SidebarBtn({ children, active, onClick }: { children: React.ReactNode; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        width: 34, height: 34, borderRadius: 9,
        border: 'none', background: active ? 'rgba(0,0,0,0.08)' : 'none',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'pointer',
        color: active ? 'var(--sidebar-active)' : 'var(--sidebar-icon)',
        transition: 'background 0.15s, color 0.15s',
      }}
      onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'rgba(0,0,0,0.05)' }}
      onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'none' }}
    >
      {children}
    </button>
  )
}
