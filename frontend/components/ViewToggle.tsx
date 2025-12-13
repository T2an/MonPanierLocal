'use client'

interface ViewToggleProps {
  view: 'map' | 'list'
  onViewChange: (view: 'map' | 'list') => void
}

export function ViewToggle({ view, onViewChange }: ViewToggleProps) {
  return (
    <div className="bg-white rounded-2xl shadow-nature p-1 flex gap-1 border-2 border-nature-200">
      <button
        onClick={() => onViewChange('map')}
        className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
          view === 'map'
            ? 'bg-nature-500 text-white shadow-nature'
            : 'text-earth-700 hover:bg-nature-50'
        }`}
        aria-label="Vue carte"
      >
        🗺️ Carte
      </button>
      <button
        onClick={() => onViewChange('list')}
        className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
          view === 'list'
            ? 'bg-nature-500 text-white shadow-nature'
            : 'text-earth-700 hover:bg-nature-50'
        }`}
        aria-label="Vue liste"
      >
        📋 Liste
      </button>
    </div>
  )
}

