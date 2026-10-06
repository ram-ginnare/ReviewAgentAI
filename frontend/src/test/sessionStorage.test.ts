import { beforeEach, describe, expect, it } from 'vitest'
import { clearStoredSession, getStoredSession, storeSession } from '../lib/sessionStorage'

describe('session storage helpers', () => {
  beforeEach(() => sessionStorage.clear())

  it('stores and clears a session per business slug', () => {
    expect(getStoredSession('reviewagentai')).toBeNull()
    storeSession('reviewagentai', 'abc')
    expect(getStoredSession('reviewagentai')).toBe('abc')
    clearStoredSession('reviewagentai')
    expect(getStoredSession('reviewagentai')).toBeNull()
  })
})
