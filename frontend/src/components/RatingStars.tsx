type Props = { value: number | null; onChange: (rating: number) => void; disabled?: boolean }

const moods = ['😞', '😕', '😐', '🙂', '🤩']

export function RatingStars({ value, onChange, disabled }: Props) {
  return (
    <div className="mx-auto w-fit" role="radiogroup" aria-label="Choose a rating from 1 to 5">
      <div className="flex justify-center gap-1.5 sm:gap-2">
        {[1, 2, 3, 4, 5].map((rating) => {
          const active = value !== null && rating <= value
          return (
            <button
              key={rating}
              type="button"
              disabled={disabled}
              role="radio"
              aria-checked={value === rating}
              aria-label={`${rating} out of 5 stars`}
              onClick={() => onChange(rating)}
              className={`ra-star-button flex h-14 w-14 items-center justify-center rounded-2xl border text-4xl leading-none transition duration-200 hover:-translate-y-1 hover:scale-105 focus:outline-none focus:ring-4 focus:ring-indigo-100 disabled:cursor-not-allowed disabled:opacity-50 sm:h-16 sm:w-16 sm:text-5xl ${active ? 'border-amber-200 bg-amber-50 text-amber-400 shadow-md shadow-amber-100' : 'border-slate-200 bg-white text-slate-200 shadow-sm hover:border-indigo-200 hover:bg-indigo-50/40'}`}
            >
              ★
            </button>
          )
        })}
      </div>
      <div className="mt-3 flex justify-center gap-1.5 sm:gap-2" aria-hidden="true">
        {moods.map((mood, index) => (
          <span key={`${mood}-${index}`} className="flex h-8 w-14 items-center justify-center text-2xl leading-none sm:w-16 sm:text-3xl">
            {mood}
          </span>
        ))}
      </div>
    </div>
  )
}
