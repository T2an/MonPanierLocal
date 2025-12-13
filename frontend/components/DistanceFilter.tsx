'use client'

interface DistanceFilterProps {
  onDistanceChange: (distance: number | null) => void
  currentDistance: number | null
  userLocation: { lat: number; lng: number; name?: string } | null
}

export function DistanceFilter({ onDistanceChange, currentDistance, userLocation }: DistanceFilterProps) {
  const distances = [5, 10, 25, 50, 100]

  if (!userLocation) {
    return null
  }

  return (
    <div className="bg-white rounded-2xl shadow-nature border-2 border-nature-200 p-4">
      <label className="block text-sm font-bold text-nature-800 mb-3 flex items-center gap-2">
        <span>📏</span>
        <span>Distance maximale</span>
      </label>
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => onDistanceChange(null)}
          className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
            currentDistance === null
              ? 'bg-nature-500 text-white shadow-nature border-2 border-nature-600'
              : 'bg-nature-50 text-earth-700 hover:bg-nature-100 border-2 border-nature-200 hover:border-nature-300'
          }`}
        >
          Tous
        </button>
        {distances.map((distance) => (
          <button
            key={distance}
            onClick={() => onDistanceChange(distance)}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              currentDistance === distance
                ? 'bg-nature-500 text-white shadow-nature border-2 border-nature-600'
                : 'bg-nature-50 text-earth-700 hover:bg-nature-100 border-2 border-nature-200 hover:border-nature-300'
            }`}
          >
            {distance} km
          </button>
        ))}
      </div>
      {userLocation.name && (
        <p className="mt-3 text-xs text-nature-600">
          📍 Recherche autour de : {userLocation.name}
        </p>
      )}
    </div>
  )
}

