'use client'

import { useState, useEffect, useCallback, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import dynamic from 'next/dynamic'
import { SearchBar } from '@/components/SearchBar'
import { FilterSidebar } from '@/components/FilterSidebar'
import { ViewToggle } from '@/components/ViewToggle'
import { ProducerList } from '@/components/ProducerList'
import { DistanceFilter } from '@/components/DistanceFilter'
import { LocationSearch } from '@/components/LocationSearch'
import { apiClient } from '@/lib/api'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import type { ProducerProfile } from '@/types'

// Import dynamique pour éviter les erreurs SSR avec Leaflet
const MapView = dynamic(() => import('@/components/MapView').then(mod => ({ default: mod.MapView })), {
  ssr: false,
})

function HomeContent() {
  const searchParams = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [view, setView] = useState<'map' | 'list'>('map')
  const [producers, setProducers] = useState<ProducerProfile[]>([])
  const [loading, setLoading] = useState(false)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number; name?: string } | null>(null)
  const [distanceFilter, setDistanceFilter] = useState<number | null>(null)
  const [distances, setDistances] = useState<number[]>([])
  const [isGeolocating, setIsGeolocating] = useState(false)

  useEffect(() => {
    // Lire les paramètres de l'URL
    const category = searchParams.get('category') || ''
    const search = searchParams.get('q') || ''
    setCategoryFilter(category)
    setSearchQuery(search)

    // Ne pas géolocaliser automatiquement - l'utilisateur doit le demander
  }, [searchParams])

  const loadProducers = useCallback(async () => {
    setLoading(true)
    try {
      let data
      if (userLocation) {
        // Utiliser la recherche par localisation
        const radius = distanceFilter || 50 // 50km par défaut si pas de filtre
        data = await apiClient.getNearbyProducers(
          userLocation.lat,
          userLocation.lng,
          radius
        )
        // Stocker les distances si disponibles
        if (data.distances) {
          setDistances(data.distances)
        } else {
          setDistances([])
        }
      } else {
        // Recherche normale sans localisation
        const params: Record<string, string> = {}
        if (categoryFilter) params.category = categoryFilter
        if (searchQuery) params.search = searchQuery
        data = await apiClient.getProducers(params)
        setDistances([])
      }
      setProducers(data.results || data)
    } catch (err: unknown) {
      setProducers([])
      setDistances([])
    } finally {
      setLoading(false)
    }
  }, [distanceFilter, userLocation, categoryFilter, searchQuery])

  useEffect(() => {
    if (view === 'list') {
      loadProducers()
    }
  }, [view, loadProducers])

  const handleUseMyLocation = () => {
    if (typeof window !== 'undefined' && navigator.geolocation) {
      setIsGeolocating(true)
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            name: 'Ma position',
          })
          setIsGeolocating(false)
        },
        () => {
          setIsGeolocating(false)
          alert('Impossible d\'accéder à votre position. Veuillez autoriser la géolocalisation.')
        }
      )
    }
  }

  const handleLocationSelect = (location: { lat: number; lng: number; name: string }) => {
    setUserLocation(location)
  }

  const handleClearLocation = () => {
    setUserLocation(null)
    setDistanceFilter(null)
    setDistances([])
  }

  return (
    <div className="relative h-screen w-full">
      {/* Barre de filtres verticale à gauche */}
      <FilterSidebar />
      
      {/* Contenu principal avec marge pour la barre latérale */}
      <div className="ml-72 h-screen relative">
        <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-3 max-w-md">
          <div className="flex flex-col gap-2">
            <SearchBar />
            <LocationSearch
              onLocationSelect={handleLocationSelect}
              currentLocation={userLocation}
              onUseMyLocation={handleUseMyLocation}
              isGeolocating={isGeolocating}
            />
            {userLocation && (
              <button
                onClick={handleClearLocation}
                className="text-xs text-nature-600 hover:text-nature-700 font-medium px-3 py-1.5 bg-nature-50 hover:bg-nature-100 rounded-xl border border-nature-200 transition-all self-start"
              >
                ✕ Effacer la localisation
              </button>
            )}
            <ViewToggle view={view} onViewChange={setView} />
          </div>
          {view === 'list' && userLocation && (
            <DistanceFilter
              onDistanceChange={setDistanceFilter}
              currentDistance={distanceFilter}
              userLocation={userLocation}
            />
          )}
        </div>
        {view === 'map' ? (
          <div className="h-full w-full">
            <MapView
              searchQuery={searchQuery}
              categoryFilter={categoryFilter}
              distanceFilter={distanceFilter}
              userLocation={userLocation}
            />
          </div>
        ) : (
          <div className="h-screen pt-32 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <LoadingSpinner size="lg" />
              </div>
            ) : (
              <ProducerList producers={producers} distances={distances} />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default function Home() {
  return (
    <Suspense fallback={
      <div className="h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    }>
      <HomeContent />
    </Suspense>
  )
}
