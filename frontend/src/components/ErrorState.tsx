export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-[20px] border border-red-200 bg-gradient-to-br from-red-50 to-white p-6 text-center shadow-soft sm:p-8" role="alert">
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-red-100 font-black text-red-600 shadow-sm">!</div>
      <p className="ra-eyebrow text-red-500">Something went wrong</p>
      <h2 className="mt-2 text-xl font-extrabold tracking-tight text-slate-950">We couldn't load this page</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-600">{message}</p>
      {onRetry && (
        <button className="ra-button ra-button-primary mt-6 w-full sm:w-auto" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}
