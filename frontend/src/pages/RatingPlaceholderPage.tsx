import { useSearchParams } from 'react-router-dom'

export function RatingPlaceholderPage() {
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session_id')

  return (
    <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-5xl items-center justify-center px-5 py-12 sm:px-6">
      <section className="w-full max-w-2xl rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm sm:p-10">
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700">Phase 4.3 next</span>
        <h1 className="mt-5 text-3xl font-bold tracking-tight">Rating screen</h1>
        <p className="mt-3 text-slate-600">The rating experience will be added in the next phase.</p>
        {sessionId && <p className="mt-5 break-all text-xs text-slate-400">Session: {sessionId}</p>}
      </section>
    </main>
  )
}
