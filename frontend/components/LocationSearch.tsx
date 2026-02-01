'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { createPortal } from 'react-dom'

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
  const [dropdownRect, setDropdownRect] = useState<{ top: number; left: number; width: number } | null>(null)

  // Define updateDropdownPosition first
  const updateDropdownPosition = useCallback(() => {
    if (!inputRef.current) return
    const rect = inputRef.current.getBoundingClientRect()
    setDropdownRect({
      top: rect.bottom + window.scrollY,
      left: rect.left + window.scrollX,
      width: rect.width,
    })
  }, [])

  // Debounce pour la recherche
  const searchLocation = useCallback(async (query: string) => {
    if (!query || query.length < 3) {
      setSuggestions([])
      setShowSuggestions(false)
      return
    }

    // Vérifier le cache
    const cacheKey = query.toLowerCase().trim()
    if (geocodeCache.has(cacheKey)) {
      const cached = geocodeCache.get(cacheKey)!
      setSuggestions(cached)
      setShowSuggestions(cached.length > 0)
      updateDropdownPosition()
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

      // Mettre en cache et limiter à 3 résultats
      const limitedLocations = locations.slice(0, 3)
      geocodeCache.set(cacheKey, limitedLocations)
      setSuggestions(limitedLocations)
      setShowSuggestions(true)
      updateDropdownPosition()
    } catch (err) {
      setError('Impossible de rechercher cette localisation')
      setSuggestions([])
      setShowSuggestions(false)
    } finally {
      setIsLoading(false)
    }
  }, [updateDropdownPosition])

  // Gérer le changement de recherche avec debounce
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }

    if (searchTerm.trim().length >= 3) {
      setShowSuggestions(true)
      updateDropdownPosition()
      searchTimeoutRef.current = setTimeout(() => {
        searchLocation(searchTerm)
      }, 300)
    } else {
      setSuggestions([])
      if (searchTerm.trim().length === 0) {
        setShowSuggestions(false)
      }
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [searchTerm, searchLocation, updateDropdownPosition])

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

  useEffect(() => {
    updateDropdownPosition()
    const handleResize = () => updateDropdownPosition()
    const handleScroll = () => updateDropdownPosition()
    
    window.addEventListener('resize', handleResize)
    window.addEventListener('scroll', handleScroll, true)
    
    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('scroll', handleScroll, true)
    }
  }, [updateDropdownPosition, showSuggestions, suggestions])

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

  const displayValue = searchTerm || (currentLocation?.name || '')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchTerm.trim().length >= 3) {
      searchLocation(searchTerm)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchTerm(value)
    setError(null)
    if (value.trim().length >= 3) {
      setShowSuggestions(true)
      updateDropdownPosition()
    } else if (value.trim().length === 0) {
      setShowSuggestions(false)
    }
  }

  return (
    <div className="relative w-full">
      {/* Champ de recherche */}
      <form onSubmit={handleSearch} className="space-y-2">
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={displayValue}
            onChange={handleInputChange}
            onFocus={() => {
              if (suggestions.length > 0 || searchTerm.trim().length >= 3) {
                setShowSuggestions(true)
                updateDropdownPosition()
              }
            }}
            placeholder="Ville, code postal..."
            className="w-full px-4 py-2.5 pl-10 pr-10 text-sm text-earth-700 bg-white border-2 border-nature-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all"
          />
          <div className="absolute inset-y-0 left-0 flex items-center pl-3">
            <svg
              className="w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          {isLoading && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-nature-500"></div>
            </div>
          )}
        </div>
        
        {/* Bouton géolocalisation */}
        <button
          type="button"
          onClick={onUseMyLocation}
          disabled={isGeolocating}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-nature-700 bg-nature-50 hover:bg-nature-100 border-2 border-nature-200 hover:border-nature-300 rounded-xl transition-all disabled:opacity-50"
        >
          {isGeolocating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-nature-500"></div>
              <span>Localisation...</span>
            </>
          ) : (
            <>
              <span>📍</span>
              <span>Utiliser ma position</span>
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-xl">
          {error}
        </div>
      )}

      {showSuggestions && suggestions.length > 0 && dropdownRect && typeof document !== 'undefined' &&
        createPortal(
          <div
            ref={suggestionsRef}
            style={{
              position: 'absolute',
              top: dropdownRect.top,
              left: dropdownRect.left,
              width: dropdownRect.width,
            }}
            className="z-[2000] mt-1 bg-white border-2 border-nature-200 rounded-2xl shadow-nature-lg overflow-hidden"
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
          </div>,
          document.body
        )
      }

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


