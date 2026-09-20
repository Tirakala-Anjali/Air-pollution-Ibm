import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, MessageCircle } from 'lucide-react'
import { askChatbot, extractError } from '../services/api'

const SUGGESTIONS = [
  'What is PM2.5?',
  'What is anomaly detection?',
  'What is Isolation Forest?',
  'What is SDG 11?',
  'How can communities reduce air pollution?',
  'What is a pollution event?',
  'What is PM10?',
]

const WELCOME = {
  role: 'bot',
  text: `Hello! I'm the AirGuard AI Assistant — a rule-based sustainability chatbot.

I can answer questions about:
• PM2.5 and PM10 particulate matter
• Anomaly detection and Isolation Forest
• Pollution events and how they are detected
• SDG 11, SDG 3, and SDG 13
• How communities can reduce air pollution

Try one of the suggested questions below, or type your own.

⚠️ I provide general educational information only. For official air-quality guidance, please consult your local environmental authority.`,
}

export default function Chatbot() {
  const [messages, setMessages] = useState([WELCOME])
  const [input,    setInput]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const bottomRef  = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const question = (text || input).trim()
    if (!question) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: question }])
    setLoading(true)
    try {
      const { answer } = await askChatbot(question)
      setMessages((prev) => [...prev, { role: 'bot', text: answer }])
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'bot', text: `Sorry, I couldn't process that: ${extractError(e)}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="card mb-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-sky-500/20 flex items-center justify-center">
          <Bot className="w-5 h-5 text-sky-400" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">AirGuard AI Assistant</p>
          <p className="text-xs text-slate-400">Rule-based sustainability chatbot · Educational use only</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'bot' && (
              <div className="w-7 h-7 rounded-full bg-sky-500/20 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5 text-sky-400" />
              </div>
            )}
            <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
              msg.role === 'user'
                ? 'bg-sky-500 text-white rounded-tr-sm'
                : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-sm'
            }`}>
              {msg.text}
            </div>
            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5 text-slate-400" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-sky-500/20 flex items-center justify-center shrink-0">
              <Bot className="w-3.5 h-3.5 text-sky-400" />
            </div>
            <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1 items-center">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="w-1.5 h-1.5 bg-sky-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      <div className="flex flex-wrap gap-2 mb-3">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => send(s)}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded-full border border-slate-600 text-slate-400 hover:text-sky-300 hover:border-sky-600 transition-colors disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask about air pollution, anomaly detection, SDGs…"
          disabled={loading}
          className="flex-1 bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 disabled:opacity-50"
        />
        <button
          onClick={() => send()}
          disabled={loading || !input.trim()}
          className="px-4 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
