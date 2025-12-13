'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

interface Location {
  display_name: string
  lat: string
  lon: string
  type: 'city' | 'postcode' | 'address' | 'other'
}

interface LocationSearchProps {
  onLocationSelect: (location: { lat: number; lng: number; name: string }) => void
  currentLocation: { lat: number; lng: number; name?: string } | null
  onUseMyLocation: () => void
  isGeolocating?: boolean
}

// Cache pour les résultats de géocodage
const geocodeCache = new Map<string, Location[]>()

export function LocationSearch({
  onLocationSelect,
  currentLocation,
  onUseMyLocation,
  isGeolocating = false,
}: LocationSearchProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [suggestions, setSuggestions] = useState<Location[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Debounce pour la recherche
  const searchLocation = useCallback(async (query: string) => {
    if (!query || query.length < 3) {
      setSuggestions([])
      return
    }

    // Vérifier le cache
    const cacheKey = query.toLowerCase().trim()
    if (geocodeCache.has(cacheKey)) {
      setSuggestions(geocodeCache.get(cacheKey)!)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // Utiliser Nominatim (OpenStreetMap) pour le géocodage
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?` +
        `q=${encodeURIComponent(query)}&` +
        `format=json&` +
        `limit=5&` +
        `countrycodes=fr&` +
        `addressdetails=1`,
        {
          headers: {
            'User-Agent': 'MonPanierLocal/1.0',
          },
        }
      )

      if (!response.ok) {
        throw new Error('Erreur de géocodage')
      }

      const data = await response.json()
      
      const locations: Location[] = data.map((item: any) => {
        let type: Location['type'] = 'other'
        if (item.type === 'city' || item.type === 'town' || item.type === 'village') {
          type = 'city'
        } else if (item.type === 'postcode') {
          type = 'postcode'
        } else if (item.type === 'house' || item.type === 'road') {
          type = 'address'
        }

        return {
          display_name: item.display_name,
          lat: item.lat,
          lon: item.lon,
          type,
        }
      })

      // Mettre en cache
      geocodeCache.set(cacheKey, locations)
      setSuggestions(locations)
    } catch (err) {
      setError('Impossible de rechercher cette localisation')
      setSuggestions([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Gérer le changement de recherche avec debounce
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }

    if (searchTerm.trim().length >= 3) {
      searchTimeoutRef.current = setTimeout(() => {
        searchLocation(searchTerm)
      }, 300)
    } else {
      setSuggestions([])
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [searchTerm, searchLocation])

  // Fermer les suggestions en cliquant à l'extérieur
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleSelect = (location: Location) => {
    onLocationSelect({
      lat: parseFloat(location.lat),
      lng: parseFloat(location.lon),
      name: location.display_name,
    })
    setSearchTerm(location.display_name)
    setShowSuggestions(false)
    setError(null)
  }

  const getLocationIcon = (type: Location['type']) => {
    switch (type) {
      case 'city':
        return '🏙️'
      case 'postcode':
        return '📮'
      case 'address':
        return '📍'
      default:
        return '🗺️'
    }
  }

  const displayValue = currentLocation?.name || searchTerm || ''

  return (
    <div className="relative w-full">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={displayValue}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            setShowSuggestions(true)
            setError(null)
          }}
          onFocus={() => setShowSuggestions(true)}
          placeholder="Rechercher une ville, code postal ou adresse..."
          className="w-full px-5 py-3 pl-12 pr-24 text-earth-700 bg-white border-3 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 shadow-nature transition-all"
        />
        <div className="absolute inset-y-0 left-0 flex items-center pl-3">
          <svg
            className="w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </div>
        <div className="absolute inset-y-0 right-0 flex items-center gap-1 pr-2">
          {isGeolocating ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-nature-500"></div>
          ) : (
            <button
              type="button"
              onClick={onUseMyLocation}
              className="px-3 py-1.5 text-xs font-semibold text-nature-600 hover:text-nature-700 hover:bg-nature-50 rounded-xl transition-all"
              title="Utiliser ma position"
            >
              📍 Moi
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-xl">
          {error}
        </div>
      )}

      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-2 bg-white border-2 border-nature-200 rounded-2xl shadow-nature-lg overflow-hidden"
        >
          {isLoading && (
            <div className="px-4 py-3 text-sm text-gray-500 text-center">
              Recherche en cours...
            </div>
          )}
          {suggestions.map((location, index) => (
            <button
              key={`${location.lat}-${location.lon}-${index}`}
              type="button"
              onClick={() => handleSelect(location)}
              className="w-full text-left px-4 py-3 hover:bg-nature-50 transition-colors border-b border-nature-100 last:border-b-0 flex items-start gap-3"
            >
              <span className="text-xl flex-shrink-0 mt-0.5">
                {getLocationIcon(location.type)}
              </span>
              <span className="flex-1 text-sm text-earth-700">
                {location.display_name}
              </span>
            </button>
          ))}
        </div>
      )}

      {currentLocation && !showSuggestions && (
        <div className="mt-2 text-xs text-nature-600 flex items-center gap-2">
          <span>📍</span>
          <span>
            {currentLocation.name || `${currentLocation.lat.toFixed(4)}, ${currentLocation.lng.toFixed(4)}`}
          </span>
        </div>
      )}
    </div>
  )
}


