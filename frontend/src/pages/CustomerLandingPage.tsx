import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { createCustomerAccess, getBusiness, recordSocialClick } from '../lib/api'
import { SocialIcon } from '../components/SocialLinks'
import type { Business, CustomerAccessResponse } from '../types/api'

type AccessSource = 'nfc' | 'qr' | 'direct'

const SOURCE_VALUES: ReadonlySet<AccessSource> = new Set(['nfc', 'qr', 'direct'])

const socialLabels: Record<string, string> = {
  FACEBOOK: 'Facebook',
  INSTAGRAM: 'Instagram',
  LINKEDIN: 'LinkedIn',
  X: 'X',
  TWITTER: 'Twitter',
  YOUTUBE: 'YouTube',
  WHATSAPP: 'WhatsApp',
  WEBSITE: 'Website',
}

function normalizeSource(value: string | null): AccessSource {
  const source = value?.trim().toLowerCase()
  return source === 'nfc' || source === 'qr' || source === 'direct' ? source : 'direct'
}


function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('') || 'R'
}


function socialIconClass(platform: string) {
  const p = platform.toUpperCase()
  switch (p) {
    case 'INSTAGRAM': return 'ra-social-icon ra-social-instagram'
    case 'FACEBOOK': return 'ra-social-icon ra-social-facebook'
    case 'YOUTUBE': return 'ra-social-icon ra-social-youtube'
    case 'WHATSAPP': return 'ra-social-icon ra-social-whatsapp'
    case 'LINKEDIN': return 'ra-social-icon ra-social-linkedin'
    case 'X':
    case 'TWITTER': return 'ra-social-icon ra-social-x'
    default: return 'ra-social-icon ra-social-default'
  }
}

function resolveLogoUrl(value: string | null | undefined) {
  if (!value) return null
  if (value.startsWith('/public/')) return value.replace(/^\/public/, '')
  return value
}

export function CustomerLandingPage() {
  const { slug } = useParams<{ slug: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const source = useMemo(() => normalizeSource(searchParams.get('source')), [searchParams])

  const [business, setBusiness] = useState<Business | null>(null)
  const [access, setAccess] = useState<CustomerAccessResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [socialLoadingId, setSocialLoadingId] = useState<number | null>(null)
  const [logoFailed, setLogoFailed] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function load() {
      if (!slug) {
        setError('Business link is missing.')
        setLoading(false)
        return
      }

      setLoading(true)
      setError('')
      try {
        const [accessResponse, businessResponse] = await Promise.all([
          createCustomerAccess(slug, source),
          getBusiness(slug),
        ])
        if (!cancelled) {
          setAccess(accessResponse)
          setBusiness(businessResponse)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unable to load this business right now.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [slug, source])

  async function handleSocialClick(id: number) {
    if (!slug) return
    setSocialLoadingId(id)
    try {
      await recordSocialClick(slug, id)
    } catch {
      // The social destination should still open if tracking is temporarily unavailable.
    } finally {
      setSocialLoadingId(null)
    }
  }

  if (loading) {
    return (
      <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-5xl items-center justify-center px-5 py-12">
        <div className="w-full max-w-xl rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />
          <h1 className="mt-5 text-xl font-bold">Loading your experience…</h1>
          <p className="mt-2 text-sm text-slate-500">Just a moment while we load the business details.</p>
        </div>
      </main>
    )
  }

  if (error || !business) {
    return (
      <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-5xl items-center justify-center px-5 py-12">
        <div className="w-full max-w-xl rounded-3xl border border-red-100 bg-white p-8 text-center shadow-sm">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-xl text-red-600">!</div>
          <h1 className="mt-5 text-2xl font-bold">We couldn't load this business</h1>
          <p className="mt-3 text-slate-600">{error || 'The business link may be invalid or unavailable.'}</p>
          <button
            onClick={() => window.location.reload()}
            className="ra-button ra-button-primary mt-6"
          >
            Try again
          </button>
        </div>
      </main>
    )
  }

  const socialLinks = business.social_links.filter((link) => link.enabled).sort((a, b) => a.display_order - b.display_order)

  return (
    <main className="mx-auto max-w-5xl px-5 py-8 sm:px-6 sm:py-12">
      <section className="mx-auto max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <div className="px-6 pb-8 pt-8 sm:px-10 sm:pt-10">
          <div className="flex flex-col items-center text-center">
            {resolveLogoUrl(business.logo_url) && !logoFailed ? (
              <img
                src={resolveLogoUrl(business.logo_url) || undefined}
                alt={`${business.name} logo`}
                className="h-24 w-24 rounded-2xl border border-slate-200 object-cover shadow-sm"
                onError={() => setLogoFailed(true)}
              />
            ) : (
              <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-slate-950 text-2xl font-bold text-white shadow-sm">
                {initials(business.name)}
              </div>
            )}

            {business.category && (
              <span className="mt-5 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-slate-600">
                {business.category}
              </span>
            )}

            <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">{business.name}</h1>
            {business.description && (
              <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">{business.description}</p>
            )}

            <div className="mt-8 grid w-full gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={() => navigate(`/r/${encodeURIComponent(business.slug)}/rating?session_id=${encodeURIComponent(access?.session_id ?? '')}`)}
                className="ra-button ra-button-primary min-h-14 w-full"
              >
                Share your experience
              </button>
              <a
                href="#social"
                className="ra-button ra-button-secondary min-h-14 w-full"
              >
                Connect with us
              </a>
            </div>

            <p className="mt-4 text-xs text-slate-500">
              Your feedback helps {business.name} improve and serve customers better.
            </p>
          </div>
        </div>

        {socialLinks.length > 0 && (
          <div id="social" className="border-t border-slate-200 bg-slate-50 px-6 py-6 sm:px-10">
            <h2 className="text-center text-sm font-bold uppercase tracking-wider text-slate-500">Follow us</h2>
            <div className="mt-4 flex flex-wrap justify-center gap-3">
              {socialLinks.map((link) => (
                <a
                  key={link.id}
                  href={link.url}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => void handleSocialClick(link.id)}
                  className="ra-button ra-button-secondary min-h-11 px-4"
                >
                  <span className={socialIconClass(link.platform)} aria-hidden="true">
                    <SocialIcon platform={link.platform} />
                  </span>
                  <span>{socialLabels[link.platform.toUpperCase()] || link.platform}</span>
                  {socialLoadingId === link.id && <span className="text-xs text-slate-400">…</span>}
                </a>
              ))}
            </div>
          </div>
        )}
      </section>
    </main>
  )
}
