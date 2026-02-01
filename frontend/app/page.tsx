'use client'

import { useState, useEffect, useCallback, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import dynamic from 'next/dynamic'
import { SearchBar } from '@/components/SearchBar'
import { FilterSidebar } from '@/components/FilterSidebar'
import { ViewToggle } from '@/components/ViewToggle'
import { ProducerList } from '@/components/ProducerList'
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
  const [categoryFilters, setCategoryFilters] = useState<string[]>([])
  const [view, setView] = useState<'map' | 'list'>('map')
  const [producers, setProducers] = useState<ProducerProfile[]>([])
  const [loading, setLoading] = useState(false)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number; name?: string } | null>(null)
  const [selectedProducer, setSelectedProducer] = useState<ProducerProfile | null>(null)
  const [distances, setDistances] = useState<number[]>([])
  const [isGeolocating, setIsGeolocating] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // Rayon fixe de 20km pour la recherche par ville
  const LOCATION_SEARCH_RADIUS = 20

  useEffect(() => {
    // Lire les paramètres de l'URL (supporte maintenant plusieurs catégories)
    const categories = searchParams.get('categories')
    if (categories) {
      setCategoryFilters(categories.split(',').filter(Boolean))
    } else {
      setCategoryFilters([])
    }
  }, [searchParams])

  const loadProducers = useCallback(async () => {
    setLoading(true)
    try {
      let data
      if (userLocation) {
        // Recherche par ville/adresse : 20km fixe autour de l'adresse
        data = await apiClient.getNearbyProducers({
          latitude: userLocation.lat,
          longitude: userLocation.lng,
          radius_km: LOCATION_SEARCH_RADIUS,
          categories: categoryFilters.length > 0 ? categoryFilters : undefined,
        })
        // Stocker les distances si disponibles
        if (data.distances) {
          setDistances(data.distances)
        } else {
          setDistances([])
        }
      } else if (selectedProducer) {
        // Recherche par nom : afficher uniquement le producteur sélectionné
        setProducers([selectedProducer])
        setDistances([])
        setLoading(false)
        return
      } else {
        // Aucune recherche active : afficher tous les producteurs
        data = await apiClient.getProducers({
          categories: categoryFilters.length > 0 ? categoryFilters : undefined
        })
        setDistances([])
      }
      
      let allProducers = data.results || data
      setProducers(allProducers)
    } catch (err: unknown) {
      setProducers([])
      setDistances([])
    } finally {
      setLoading(false)
    }
  }, [userLocation, selectedProducer, categoryFilters])

  useEffect(() => {
    if (view === 'list') {
      loadProducers()
    }
  }, [view, selectedProducer, userLocation, categoryFilters, loadProducers])

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
    // Effacer la recherche par nom quand on sélectionne une ville
    setSelectedProducer(null)
  }

  const handleClearLocation = () => {
    setUserLocation(null)
    setDistances([])
  }

  const handleProducerSelect = (producer: ProducerProfile | null) => {
    setSelectedProducer(producer)
    // Effacer la recherche par ville quand on sélectionne un producteur
    if (producer) {
      setUserLocation(null)
      setDistances([])
    }
  }

  return (
    <div className="relative h-screen w-full">
      {/* Barre de filtres verticale à gauche */}
      <FilterSidebar 
        isCollapsed={sidebarCollapsed} 
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      >
        <div className="flex flex-col gap-5">
          {/* Recherche par nom */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-nature-700 uppercase tracking-wide flex items-center gap-2">
              <span>👤</span>
              <span>Par nom de producteur</span>
            </h3>
            <SearchBar onProducerSelect={handleProducerSelect} />
          </div>

          {/* Séparateur */}
          <div className="border-t-2 border-nature-200 border-dashed" />

          {/* Recherche par adresse */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-nature-700 uppercase tracking-wide flex items-center gap-2">
              <span>📍</span>
              <span>Par adresse</span>
            </h3>
            <LocationSearch
              onLocationSelect={handleLocationSelect}
              currentLocation={userLocation}
              onUseMyLocation={handleUseMyLocation}
              isGeolocating={isGeolocating}
            />
            {userLocation && (
              <button
                onClick={handleClearLocation}
                className="text-xs text-nature-600 hover:text-nature-700 font-medium px-3 py-1.5 bg-nature-50 hover:bg-nature-100 rounded-xl border border-nature-200 transition-all"
              >
                ✕ Effacer
              </button>
            )}
          </div>
        </div>
      </FilterSidebar>
      
      {/* Contenu principal avec marge pour la barre latérale */}
      <div className={`h-screen relative transition-all duration-300 ${sidebarCollapsed ? 'ml-0' : 'ml-96'}`}>
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000]">
          <ViewToggle view={view} onViewChange={setView} />
        </div>
        {view === 'map' ? (
          <div className="h-full w-full">
            <MapView
              categoryFilters={categoryFilters}
              userLocation={userLocation}
              selectedProducer={selectedProducer}
              locationSearchRadius={LOCATION_SEARCH_RADIUS}
            />
          </div>
        ) : (
          <div className="h-screen pt-6 overflow-y-auto">
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
