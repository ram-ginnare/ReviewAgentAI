import type { User } from '../types/api'

const TOKEN_KEY = 'reviewagentai_access_token'
const USER_KEY = 'reviewagentai_auth_user'

export type AuthSession = {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export function storeAuth(session: AuthSession) {
  sessionStorage.setItem(TOKEN_KEY, session.access_token)
  sessionStorage.setItem(USER_KEY, JSON.stringify(session.user))
}

export function getAuthToken() {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function getStoredUser(): User | null {
  const raw = sessionStorage.getItem(USER_KEY)
  if (!raw) return null
  try { return JSON.parse(raw) as User } catch { return null }
}

export function clearAuth() {
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(USER_KEY)
}
