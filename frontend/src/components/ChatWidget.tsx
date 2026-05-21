import { CSSProperties, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import type { BotState } from '../App'
import { WavRecorder } from '../utils/wavRecorder'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface Message {
  id: string
  role: 'user' | 'bot'
  text: string
}

interface Props {
  setBotState: (s: BotState) => void
}

export default function ChatWidget({ setBotState }: Props) {
  const [messages, setMessages]         = useState<Message[]>([])
  const [drawerOpen, setDrawerOpen]     = useState(false)
  const [textInput, setTextInput]       = useState('')
  const [isRecording, setIsRecording]   = useState(false)
  const [loading, setLoading]           = useState(false)
  const [tickerText, setTickerText]     = useState('')

  const recorderRef   = useRef<WavRecorder | null>(null)
  const streamRef     = useRef<MediaStream | null>(null)
  const bottomRef     = useRef<HTMLDivElement>(null)

  // Yangi xabar kelganda avtomatik pastga scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const addMsg = (role: Message['role'], text: string) =>
    setMessages(prev => [...prev, { id: `${Date.now()}-${Math.random()}`, role, text }])

  /* ─── Ovozli yozish: bir marta bosib start, yana bosib stop ─── */
  const toggleRecording = async () => {
    if (isRecording) {
      await stopRecording()
    } else {
      await startRecording()
    }
  }

  const startRecording = async () => {
    if (loading) return
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current   = stream
      recorderRef.current = new WavRecorder(stream)
      setIsRecording(true)
      setBotState('listening')
    } catch {
      alert('Mikrofonga ruxsat berilmadi. Brauzer sozlamalarini tekshiring.')
    }
  }

  const stopRecording = async () => {
    if (!recorderRef.current) return
    const wavBlob = recorderRef.current.stop()
    streamRef.current?.getTracks().forEach(t => t.stop())
    recorderRef.current = null
    streamRef.current   = null
    setIsRecording(false)
    setBotState('thinking')
    await sendVoice(wavBlob)
  }

  /* ─── Ovozli so'rov ─── */
  const sendVoice = async (blob: Blob) => {
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('audio', blob, 'audio.wav')

      const res = await fetch(`${API}/chat/voice`, { method: 'POST', body: fd })
      if (!res.ok) throw new Error(await res.text())

      const data: {
        question: string
        answer: string
        audio: string
        audio_type: string
      } = await res.json()

      // Chat tarixiga qo'shish
      if (data.question) addMsg('user', `🎤 ${data.question}`)
      addMsg('bot', data.answer)
      setTickerText(data.answer)

      playBase64(data.audio, data.audio_type || 'audio/mpeg')
    } catch (e) {
      console.error('Voice xato:', e)
      addMsg('bot', '❌ Xato yuz berdi. Qayta urinib ko\'ring.')
      setBotState('idle')
    } finally {
      setLoading(false)
    }
  }

  /* ─── Matnli so'rov ─── */
  const sendText = async () => {
    const msg = textInput.trim()
    if (!msg || loading) return
    setTextInput('')
    addMsg('user', msg)
    setLoading(true)
    setBotState('thinking')
    try {
      const res = await fetch(`${API}/chat/text`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message: msg }),
      })
      const data: { answer: string } = await res.json()
      addMsg('bot', data.answer)
      setTickerText(data.answer)
      setBotState('speaking')
      setTimeout(() => setBotState('idle'), 6000)
    } catch (e) {
      console.error('Text xato:', e)
      addMsg('bot', '❌ Xato yuz berdi.')
      setBotState('idle')
    } finally {
      setLoading(false)
    }
  }

  const playBase64 = (b64: string, mimeType = 'audio/mpeg') => {
    const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0))
    const blob  = new Blob([bytes], { type: mimeType })
    const url   = URL.createObjectURL(blob)
    const audio = new Audio(url)
    setBotState('speaking')
    audio.onended = () => { setBotState('idle'); URL.revokeObjectURL(url) }
    audio.onerror = () => { setBotState('idle'); URL.revokeObjectURL(url) }
    audio.play()
  }

  const tickerDuration = `${Math.max(tickerText.length * 0.09, 10)}s`

  return (
    <>
      {/* ── Ticker ── */}
      {tickerText && (
        <div
          className="absolute left-0 right-0 overflow-hidden pointer-events-none"
          style={{ bottom: 'calc(5rem + env(safe-area-inset-bottom, 0px))' }}
        >
          <span
            className="ticker-text text-white text-base sm:text-xl font-semibold drop-shadow-lg px-4 sm:px-6"
            style={{ '--ticker-duration': tickerDuration } as CSSProperties}
            onAnimationEnd={() => setTickerText('')}
          >
            {tickerText}
          </span>
        </div>
      )}

      {/* ── Chap pastda: Telegram tugmasi ── */}
      <div
        className="absolute left-4 sm:left-6"
        style={{ bottom: 'calc(1.5rem + env(safe-area-inset-bottom, 0px))' }}
      >
        <motion.a
          href="https://t.me/EcoEkspertizaAI_bot"
          target="_blank"
          rel="noopener noreferrer"
          whileHover={{ scale: 1.07 }}
          whileTap={{ scale: 0.93 }}
          style={{
            width:          '4.5rem',
            height:         '4.5rem',
            borderRadius:   '50%',
            background:     '#229ED9',
            border:         '3px solid rgba(255,255,255,0.25)',
            color:          'white',
            cursor:         'pointer',
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'center',
            flexDirection:  'column',
            gap:            '2px',
            textDecoration: 'none',
          }}
        >
          {/* Telegram SVG icon */}
          <svg width="28" height="28" viewBox="0 0 24 24" fill="white">
            <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
          </svg>
        </motion.a>
      </div>

      {/* ── Pastki boshqaruv: Start + Chat ── */}
      <div
        className="absolute right-4 sm:right-6 flex items-end gap-3 sm:gap-4"
        style={{ bottom: 'calc(1.5rem + env(safe-area-inset-bottom, 0px))' }}
      >

        {/* 🔴 START / STOP tugmasi */}
        <motion.button
          onClick={() => { void toggleRecording() }}
          disabled={loading}
          whileHover={{ scale: loading ? 1 : 1.07 }}
          whileTap={{ scale: 0.93 }}
          animate={isRecording
            ? { boxShadow: ['0 0 0px #ef4444', '0 0 32px #ef4444', '0 0 0px #ef4444'] }
            : {}}
          transition={isRecording ? { duration: 0.75, repeat: Infinity } : {}}
          style={{
            width:        '4.5rem',
            height:       '4.5rem',
            borderRadius: '50%',
            background:   isRecording ? '#dc2626' : '#ef4444',
            border:       '3px solid rgba(255,255,255,0.25)',
            cursor:       loading ? 'not-allowed' : 'pointer',
            opacity:      loading && !isRecording ? 0.55 : 1,
            display:      'flex',
            alignItems:   'center',
            justifyContent: 'center',
            flexDirection: 'column',
            gap:          '0',
          }}
        >
          <span style={{
            color:       'white',
            fontWeight:  800,
            fontSize:    isRecording ? '0.6rem' : '0.75rem',
            letterSpacing: '0.08em',
            lineHeight:  1,
          }}>
            {isRecording ? 'TO\'XTAT' : 'START'}
          </span>
        </motion.button>

        {/* 💬 Chat drawer toggle — xuddi Start bilan bir xil razmer */}
        <motion.button
          whileHover={{ scale: 1.07 }}
          whileTap={{ scale: 0.93 }}
          onClick={() => setDrawerOpen(v => !v)}
          style={{
            width:          '4.5rem',
            height:         '4.5rem',
            borderRadius:   '50%',
            background:     drawerOpen ? '#1d4ed8' : '#2563eb',
            border:         '3px solid rgba(255,255,255,0.25)',
            color:          'white',
            fontSize:       '1.5rem',
            cursor:         'pointer',
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'center',
          }}
        >
          💬
        </motion.button>
      </div>

      {/* ── Chat Drawer (o'ngdan chiqadi) ── */}
      <AnimatePresence>
        {drawerOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setDrawerOpen(false)}
              className="absolute inset-0"
              style={{ background: 'rgba(0,0,0,0.35)', backdropFilter: 'blur(3px)' }}
            />

            {/* Panel */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 220 }}
              className="absolute top-0 right-0 h-full flex flex-col"
              style={{
                width:        'min(400px, 100vw)',
                background:   'rgba(10,18,35,0.94)',
                backdropFilter: 'blur(24px)',
                borderLeft:   '1px solid rgba(255,255,255,0.08)',
              }}
            >
              {/* Header */}
              <div
                className="flex items-center justify-between flex-shrink-0"
                style={{
                  padding:      '1rem 1.25rem',
                  borderBottom: '1px solid rgba(255,255,255,0.08)',
                }}
              >
                <span className="text-white font-semibold text-base">Suhbat</span>
                <button
                  onClick={() => setDrawerOpen(false)}
                  className="text-white/50 hover:text-white transition-colors text-lg leading-none"
                >
                  ✕
                </button>
              </div>

              {/* Xabarlar ro'yxati */}
              <div className="flex-1 overflow-y-auto flex flex-col gap-3" style={{ padding: '1rem 1.25rem' }}>
                {messages.length === 0 && (
                  <p className="text-center text-white/25 text-sm mt-10 select-none">
                    Savol yuboring yoki<br />mikrofon tugmasini bosing
                  </p>
                )}

                {messages.map(msg => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className="max-w-[82%] text-sm text-white leading-relaxed break-words"
                      style={{
                        padding:      '0.75rem 1.1rem',
                        background:   msg.role === 'user' ? '#2563eb' : 'rgba(255,255,255,0.10)',
                        borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                      }}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}

                {/* Yuklash ko'rsatkichi */}
                {loading && (
                  <div className="flex justify-start">
                    <div
                      className="px-4 py-2 text-white/40 text-lg tracking-widest"
                      style={{
                        background:   'rgba(255,255,255,0.07)',
                        borderRadius: '18px 18px 18px 4px',
                      }}
                    >
                      •••
                    </div>
                  </div>
                )}

                <div ref={bottomRef} />
              </div>

              {/* Matn kiritish */}
              <div
                className="flex items-end gap-3 flex-shrink-0"
                style={{
                  padding:   '1rem 1.25rem',
                  borderTop: '1px solid rgba(255,255,255,0.08)',
                }}
              >
                <input
                  type="text"
                  value={textInput}
                  onChange={e => setTextInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && void sendText()}
                  placeholder="Savol yozing..."
                  disabled={loading}
                  className="flex-1 text-sm text-white placeholder-white/30 outline-none"
                  style={{
                    background:   'rgba(255,255,255,0.07)',
                    border:       '1px solid rgba(255,255,255,0.15)',
                    borderRadius: '14px',
                    padding:      '0.75rem 1.1rem',
                    lineHeight:   '1.5',
                    transition:   'border-color 0.15s',
                  }}
                  onFocus={e => (e.target.style.borderColor = 'rgba(59,130,246,0.6)')}
                  onBlur={e  => (e.target.style.borderColor = 'rgba(255,255,255,0.15)')}
                />
                <motion.button
                  whileHover={{ scale: 1.07 }}
                  whileTap={{ scale: 0.88 }}
                  onClick={() => void sendText()}
                  disabled={loading || !textInput.trim()}
                  style={{
                    width:          '2.8rem',
                    height:         '2.8rem',
                    borderRadius:   '50%',
                    background:     textInput.trim() && !loading ? '#2563eb' : 'rgba(255,255,255,0.08)',
                    border:         'none',
                    color:          'white',
                    fontSize:       '1.1rem',
                    cursor:         textInput.trim() && !loading ? 'pointer' : 'default',
                    display:        'flex',
                    alignItems:     'center',
                    justifyContent: 'center',
                    flexShrink:     0,
                    transition:     'background 0.2s',
                  }}
                >
                  ➤
                </motion.button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
