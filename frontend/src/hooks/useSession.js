/**
 * Persists and retrieves the current analysis session_id
 * from sessionStorage so pages stay in sync on navigation.
 */
import { useState, useEffect } from 'react'

export function useSession() {
  const [sessionId, setSessionIdState] = useState(
    () => sessionStorage.getItem('airguard_session') || null
  )

  const setSessionId = (id) => {
    if (id) {
      sessionStorage.setItem('airguard_session', id)
    } else {
      sessionStorage.removeItem('airguard_session')
    }
    setSessionIdState(id)
  }

  return { sessionId, setSessionId }
}
