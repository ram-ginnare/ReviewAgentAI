const keyFor = (slug: string) => `reviewagentai:session:${slug}`

export function getStoredSession(slug: string): string | null {
  return sessionStorage.getItem(keyFor(slug))
}

export function storeSession(slug: string, sessionId: string): void {
  sessionStorage.setItem(keyFor(slug), sessionId)
}

export function clearStoredSession(slug: string): void {
  sessionStorage.removeItem(keyFor(slug))
}
