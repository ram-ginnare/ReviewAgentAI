import { useCallback, useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { AppShell } from '../components/AppShell'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'
import { RatingStars } from '../components/RatingStars'
import { SocialLinks } from '../components/SocialLinks'
import { api, ApiClientError } from '../lib/api'
import { copyText } from '../lib/clipboard'
import { clearStoredSession, getStoredSession, storeSession } from '../lib/sessionStorage'
import type { Business, GeneratedReview, SocialLink } from '../types/api'

type Stage = 'landing' | 'rating' | 'positive' | 'private' | 'success' | 'expired'
type Preferences = {
  professional_staff: boolean
  reliable_service: boolean
  good_ambiance: boolean
  affordable_pricing: boolean
}

const emptyPreferences: Preferences = {
  professional_staff: false,
  reliable_service: false,
  good_ambiance: false,
  affordable_pricing: false,
}

const preferenceLabels: Array<[keyof Preferences, string, string]> = [
  ['professional_staff', 'Professional staff', 'The team was professional and helpful.'],
  ['reliable_service', 'Reliable Service', 'The service was dependable and smooth.'],
  ['good_ambiance', 'Good Ambiance', 'The atmosphere was pleasant and welcoming.'],
  ['affordable_pricing', 'Affordable Pricing', 'The pricing felt reasonable and good value.'],
]

function resolveLogoUrl(value: string | null | undefined) {
  if (!value) return null
  if (value.startsWith('/public/')) return value.replace(/^\/public/, '')
  return value
}

function sourceFromQuery(search: string): 'nfc' | 'qr' | 'direct' {
  const source = new URLSearchParams(search).get('source')?.toLowerCase()
  return source === 'nfc' || source === 'qr' ? source : 'direct'
}

export function CustomerPage() {
  const { slug = '' } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [business, setBusiness] = useState<Business | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [stage, setStage] = useState<Stage>('landing')
  const [rating, setRating] = useState<number | null>(null)
  const [preferences, setPreferences] = useState<Preferences>(emptyPreferences)
  const [customerComment, setCustomerComment] = useState('')
  const [reviews, setReviews] = useState<GeneratedReview[]>([])
  const [selectedReviewId, setSelectedReviewId] = useState<number | null>(null)
  const [privateComment, setPrivateComment] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [copied, setCopied] = useState(false)
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [logoFailed, setLogoFailed] = useState(false)

  const selectedReview = useMemo(() => reviews.find((review) => review.id === selectedReviewId) || null, [reviews, selectedReviewId])

  const load = useCallback(async () => {
    if (!slug) {
      setError('The business link is missing a valid slug.')
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const businessData = await api.getBusiness(slug)
      setBusiness(businessData)

      const source = sourceFromQuery(location.search)
      let existingSession = getStoredSession(slug)
      let flow = existingSession ? await api.getFlow(existingSession).catch(() => null) : null

      if (!flow || flow.expired) {
        const access = await api.createAccess(slug, source)
        existingSession = access.session_id
        storeSession(slug, existingSession)
        flow = await api.getFlow(existingSession)
      }

      setSessionId(existingSession)
      setRating(flow.rating)
      if (flow.expired) {
        setStage('expired')
      } else if (flow.status === 'completed') {
        setStage('success')
        setSuccessMessage('Thanks for sharing your experience.')
      } else if (flow.rating === null) {
        setStage('landing')
      } else if (flow.rating >= 4) {
        setStage('positive')
      } else {
        setStage('private')
      }
    } catch (err) {
      if (err instanceof ApiClientError && err.message.toLowerCase().includes('business not found')) {
        setError('This business link is not available. Please check the link and try again.')
      } else if (err instanceof ApiClientError) {
        setError(err.message)
      } else {
        setError('We could not load this business. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }, [location.search, slug])

  useEffect(() => {
    void load()
  }, [load])

  const startRating = () => {
    setNotice(null)
    setStage('rating')
  }

  const chooseRating = async (nextRating: number) => {
    if (!sessionId || busy) return
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      const response = await api.rateSession(sessionId, nextRating)
      setRating(nextRating)
      await api.recordEvent(slug, 'RATING_SELECTED', nextRating, { session_id: sessionId })
      if (response.next_step === 'positive_review') {
        setStage('positive')
      } else {
        setStage('private')
      }
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'We could not save your rating. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  const generateReviews = async () => {
    if (!sessionId || !rating) return
    const hasPreference = Object.values(preferences).some(Boolean)
    if (!hasPreference && !customerComment.trim()) {
      setNotice('Please select at least one option or tell us a little more about your experience.')
      return
    }

    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      const response = await api.generatePositiveReviews(sessionId, {
        ...preferences,
        customer_comment: customerComment.trim() || undefined,
      })
      if (!response.reviews.length) {
        setNotice('We could not find a review suggestion yet. Please try again.')
        return
      }
      setReviews(response.reviews)
      setSelectedReviewId(response.reviews[0].id)
      setStage('positive')
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'We could not generate review suggestions. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  const submitPrivateFeedback = async () => {
    if (!sessionId || privateComment.trim().length < 3) {
      setNotice('Please enter at least 3 characters so the business can understand your feedback.')
      return
    }
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      const response = await api.submitPrivateFeedback(sessionId, privateComment.trim())
      await api.recordEvent(slug, 'PRIVATE_FEEDBACK_SUBMITTED', rating || undefined, { session_id: sessionId })
      clearStoredSession(slug)
      setSuccessMessage(response.acknowledgement)
      setStage('success')
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'We could not submit your feedback. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  const copyAndOpenGoogle = async () => {
    if (!sessionId || !selectedReview) return

    // Open a blank tab synchronously so browser popup blockers do not reject the later navigation.
    const popup = window.open('', '_blank')
    setBusy(true)
    setError(null)
    setNotice(null)
    setCopied(false)

    try {
      const finalText = selectedReview.generated_review.trim()
      if (!finalText) throw new Error('The selected review is empty.')

      const copiedSuccessfully = await copyText(finalText)
      if (!copiedSuccessfully) {
        popup?.close()
        setNotice('We could not copy the review to your clipboard. Please copy the text manually before opening Google.')
        return
      }

      const response = await api.selectGoogleReview(sessionId, selectedReview.id, finalText)
      await api.recordEvent(slug, 'REVIEW_SELECTED', rating || undefined, { session_id: sessionId, review_id: selectedReview.id })
      await api.recordEvent(slug, 'GOOGLE_HANDOFF', rating || undefined, {
        session_id: sessionId,
        review_id: selectedReview.id,
        device_type: response.device_type,
      })

      setCopied(true)
      clearStoredSession(slug)
      setSuccessMessage('Your review text was copied. Google is opening now. Please paste it into Google and submit it yourself.')
      setStage('success')
      if (popup) {
        popup.location.href = response.google_review_url
      } else {
        window.location.assign(response.google_review_url)
      }
    } catch (err) {
      popup?.close()
      setError(err instanceof ApiClientError ? err.message : 'We could not prepare the Google review handoff. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  const updateSelectedReview = (reviewId: number, text: string) => {
    setReviews((current) => current.map((review) => (review.id === reviewId ? { ...review, generated_review: text } : review)))
  }

  const handleSocialClick = (link: SocialLink) => {
    void api.trackSocialClick(slug, link.id, sessionId || undefined)
  }

  const restart = () => {
    clearStoredSession(slug)
    navigate(`/r/${encodeURIComponent(slug)}?source=${sourceFromQuery(location.search)}`)
    window.location.reload()
  }

  if (loading) return <AppShell><LoadingState /></AppShell>
  if (error && !business) return <AppShell><ErrorState message={error} onRetry={() => void load()} /></AppShell>
  if (!business) return <AppShell><ErrorState message="Business information is unavailable." onRetry={() => void load()} /></AppShell>

  return (
    <AppShell businessName={business.name}>
      {error && <div className="mb-5"><ErrorState message={error} /></div>}
      {notice && <div className="mb-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900" role="status">{notice}</div>}

      {stage === 'landing' && (
        <section className="ra-card relative overflow-hidden p-6 sm:p-9">
          <div className="text-center">
            {resolveLogoUrl(business.logo_url) && !logoFailed ? (
              <img
                src={resolveLogoUrl(business.logo_url) || undefined}
                alt={`${business.name} logo`}
                className="mx-auto h-20 w-20 rounded-2xl object-cover ring-1 ring-slate-200"
                onError={() => setLogoFailed(true)}
              />
            ) : (
              <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-slate-900 text-2xl font-bold text-white" aria-hidden="true">
                {business.name.slice(0, 1).toUpperCase()}
              </div>
            )}
            <p className="mt-5 text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{business.category || 'Business'}</p>
            <h1 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">{business.name}</h1>
            {business.description && <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-slate-600">{business.description}</p>}
            <button onClick={startRating} className="ra-button ra-button-primary mt-8 w-full sm:w-auto sm:min-w-64">
              Share your experience
            </button>
          </div>
          <SocialLinks links={business.social_links} onClick={handleSocialClick} />
        </section>
      )}

      {stage === 'rating' && (
        <section className="ra-card relative overflow-hidden p-6 sm:p-9">
          <div className="text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Your experience</p>
            <h1 className="mt-2 text-3xl font-extrabold tracking-tight">How was your experience?</h1>
            <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-slate-600">Choose the rating that best reflects your visit. We’ll guide you to the right next step.</p>
            <div className="mt-8"><RatingStars value={rating} onChange={(value) => void chooseRating(value)} disabled={busy} /></div>
            <div className="mt-5 flex justify-center gap-2 text-sm text-slate-500" aria-live="polite">
              {rating ? <span>{rating}/5 selected</span> : <span>Select a star rating</span>}
            </div>
          </div>
        </section>
      )}

      {stage === 'positive' && (
        <section className="space-y-5">
          {reviews.length === 0 ? (
            <div className="ra-card relative overflow-hidden p-6 sm:p-9">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{rating}/5 experience</p>
              <h1 className="mt-2 text-3xl font-extrabold tracking-tight">What stood out to you?</h1>
              <p className="mt-3 text-sm leading-6 text-slate-600">Pick anything that genuinely describes your experience. You can also add your own words.</p>
              <div className="mt-6 grid gap-3 sm:grid-cols-2">
                {preferenceLabels.map(([key, label, helper]) => (
                  <label key={key} className={`cursor-pointer rounded-2xl border p-4 transition duration-200 ${preferences[key] ? 'border-indigo-300 bg-indigo-50 ring-2 ring-indigo-100' : 'border-slate-200 bg-white hover:border-indigo-200 hover:bg-indigo-50/40'}`}>
                    <span className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={preferences[key]}
                        onChange={(event) => setPreferences((current) => ({ ...current, [key]: event.target.checked }))}
                        className="mt-1 h-5 w-5 rounded border-slate-300 text-slate-950 focus:ring-slate-300"
                      />
                      <span>
                        <span className="block font-semibold text-slate-900">{label}</span>
                        <span className="mt-1 block text-xs leading-5 text-slate-500">{helper}</span>
                      </span>
                    </span>
                  </label>
                ))}
              </div>
              <label className="mt-5 block">
                <span className="text-sm font-semibold text-slate-900">Anything else? <span className="font-normal text-slate-400">(optional)</span></span>
                <textarea
                  value={customerComment}
                  onChange={(event) => setCustomerComment(event.target.value.slice(0, 1000))}
                  rows={4}
                  maxLength={1000}
                  placeholder="Add a few words in your own voice…"
                  className="mt-2 w-full resize-none rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 outline-none transition focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
                />
                <span className="mt-1 block text-right text-xs text-slate-400">{customerComment.length}/1000</span>
              </label>
              <button disabled={busy} onClick={() => void generateReviews()} className="ra-button ra-button-primary mt-5 w-full">
                {busy ? 'Creating review suggestions…' : 'Create review suggestions'}
              </button>
            </div>
          ) : (
            <>
              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sm:p-8">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Your {rating}/5 review</p>
                    <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Choose your favorite version</h1>
                  </div>
                  <button type="button" onClick={() => setReviews([])} className="ra-button ra-button-secondary min-h-10 px-4 text-xs">Change my input</button>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">You can edit any suggestion. Select the version that feels most like your experience.</p>
              </div>
              <div className="space-y-4">
                {reviews.map((review, index) => {
                  const selected = selectedReviewId === review.id
                  return (
                    <article key={review.id} className={`rounded-3xl border bg-white p-5 shadow-sm transition sm:p-6 ${selected ? 'border-indigo-300 bg-indigo-50/30 ring-4 ring-indigo-100' : 'border-slate-200'}`}>
                      <div className="flex items-center justify-between gap-3">
                        <button type="button" onClick={() => setSelectedReviewId(review.id)} className="ra-button ra-button-secondary min-h-10 gap-3 px-3 text-left">
                          <span className={`flex h-7 w-7 items-center justify-center rounded-full text-xs ${selected ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-500'}`}>{index + 1}</span>
                          {selected ? 'Selected review' : 'Select this review'}
                        </button>
                        <span className="text-xs text-slate-400">Editable</span>
                      </div>
                      <textarea
                        value={review.generated_review}
                        onChange={(event) => updateSelectedReview(review.id, event.target.value.slice(0, 2000))}
                        rows={5}
                        maxLength={2000}
                        aria-label={`Review suggestion ${index + 1}`}
                        className="mt-4 w-full resize-none rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-7 outline-none focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
                      />
                    </article>
                  )
                })}
              </div>
              <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-soft sm:p-6">
                <button disabled={busy || !selectedReview?.generated_review.trim()} onClick={() => void copyAndOpenGoogle()} className="ra-button ra-button-primary w-full">
                  {busy ? 'Preparing Google…' : 'Copy & Open Google'}
                </button>
                <p className="mt-3 text-center text-xs leading-5 text-slate-500">Your review is never submitted automatically. Google will open after your text is copied.</p>
                {copied && <p className="mt-2 text-center text-sm font-semibold text-emerald-700" role="status">Review copied successfully.</p>}
              </div>
            </>
          )}
        </section>
      )}

      {stage === 'private' && (
        <section className="ra-card relative overflow-hidden p-6 sm:p-9">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Private feedback</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Tell us what could be better</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">Your feedback will go privately to the business. It will not be posted as a public Google review.</p>
          <label className="mt-6 block">
            <span className="text-sm font-semibold text-slate-900">Your comments</span>
            <textarea
              value={privateComment}
              onChange={(event) => setPrivateComment(event.target.value.slice(0, 2000))}
              rows={7}
              maxLength={2000}
              placeholder="Please tell us what happened or what you would like the business to improve…"
              className="mt-2 w-full resize-none rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-7 outline-none focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
            />
            <span className="mt-1 block text-right text-xs text-slate-400">{privateComment.length}/2000</span>
          </label>
          <button disabled={busy} onClick={() => void submitPrivateFeedback()} className="ra-button ra-button-primary mt-5 w-full">
            {busy ? 'Sending privately…' : 'Send private feedback'}
          </button>
          <p className="mt-3 text-center text-xs text-slate-500">Rating: {rating}/5</p>
        </section>
      )}

      {stage === 'success' && (
        <section className="rounded-3xl border border-emerald-200 bg-white p-7 text-center shadow-soft sm:p-10" role="status">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 text-2xl text-emerald-700">✓</div>
          <h1 className="mt-5 text-3xl font-extrabold tracking-tight">Thank you!</h1>
          <p className="mx-auto mt-3 max-w-lg text-sm leading-7 text-slate-600">{successMessage || 'Thanks for sharing your experience.'}</p>
          <button onClick={restart} className="ra-button ra-button-primary mt-7">Start a new review</button>
        </section>
      )}

      {stage === 'expired' && (
        <section className="ra-card p-7 text-center sm:p-10">
          <h1 className="text-3xl font-extrabold tracking-tight">This session has expired</h1>
          <p className="mx-auto mt-3 max-w-md text-sm leading-7 text-slate-600">For your security, review sessions are temporary. Start a new session to continue.</p>
          <button onClick={restart} className="ra-button ra-button-primary mt-7">Start again</button>
        </section>
      )}
    </AppShell>
  )
}
