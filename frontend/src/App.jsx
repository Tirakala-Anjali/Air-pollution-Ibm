import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'

import Sidebar    from './components/Sidebar'
import Topbar     from './components/Topbar'

import Dashboard    from './pages/Dashboard'
import Trends       from './pages/Trends'
import Events       from './pages/Events'
import EventDetail  from './pages/EventDetail'
import UploadData   from './pages/UploadData'
import Chatbot      from './pages/Chatbot'
import Awareness    from './pages/Awareness'
import ResponsibleAI from './pages/ResponsibleAI'
import About        from './pages/About'

const PAGE_TITLES = {
  '/':              'Dashboard',
  '/trends':        'Pollution Trends',
  '/events':        'Pollution Events',
  '/upload':        'Upload Data',
  '/chat':          'AI Assistant',
  '/awareness':     'Environmental Awareness',
  '/responsible-ai':'Responsible AI',
  '/about':         'About Project',
}

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  // derive page title (handles /events/123 → Events)
  const base = '/' + location.pathname.split('/')[1]
  const title = PAGE_TITLES[base] || 'AirGuard'

  // Close sidebar on route change (mobile)
  useEffect(() => setSidebarOpen(false), [location.pathname])

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar mobileOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar onMenuClick={() => setSidebarOpen(true)} title={title} />

        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Routes>
            <Route path="/"              element={<Dashboard />} />
            <Route path="/trends"        element={<Trends />} />
            <Route path="/events"        element={<Events />} />
            <Route path="/events/:id"    element={<EventDetail />} />
            <Route path="/upload"        element={<UploadData />} />
            <Route path="/chat"          element={<Chatbot />} />
            <Route path="/awareness"     element={<Awareness />} />
            <Route path="/responsible-ai" element={<ResponsibleAI />} />
            <Route path="/about"         element={<About />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  )
}
