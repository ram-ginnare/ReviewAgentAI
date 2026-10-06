import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-5xl items-center px-5 py-12 sm:px-6">
      <section className="mx-auto w-full max-w-2xl rounded-3xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
        <span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700">
          Phase 4.2
        </span>
        <h1 className="mt-5 text-3xl font-bold tracking-tight sm:text-4xl">Customer landing page is ready.</h1>
        <p className="mt-4 leading-7 text-slate-600">
          Open a business customer URL such as <code className="rounded bg-slate-100 px-1.5 py-0.5 text-sm">/r/reviewagentai</code> to load the real business profile from your FastAPI backend.
        </p>
        <Link
          to="/r/reviewagentai"
          className="ra-button ra-button-primary mt-7"
        >
          Open demo business
        </Link>
      </section>
    </main>
  )
}
