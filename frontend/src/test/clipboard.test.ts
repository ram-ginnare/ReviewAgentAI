import { describe, expect, it } from 'vitest'
import { copyText } from '../lib/clipboard'

describe('copyText', () => {
  it('returns false for empty text', async () => {
    expect(await copyText('   ')).toBe(false)
  })
})
