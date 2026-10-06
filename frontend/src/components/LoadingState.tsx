export function LoadingState({ label = 'Loading your experience…' }: { label?: string }) {
  return (
    <div className="flex min-h-[320px] items-center justify-center" role="status" aria-live="polite">
      <div className="ra-card flex items-center gap-4 px-6 py-5">
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-100 border-t-indigo-600" />
        <span className="text-sm font-semibold text-slate-600">{label}</span>
      </div>
    </div>
  )
}
