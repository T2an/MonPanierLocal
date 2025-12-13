'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { apiClient } from '@/lib/api'
import { MAP_DEFAULTS, CLUSTERING_THRESHOLD } from '@/lib/constants'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorMessage } from './ErrorMessage'
import type { ProducerProfile } from '@/types'

// Import dynamique de tous les composants Leaflet pour éviter les erreurs SSR
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false })
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false })
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false })
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false })

// Composant qui utilise useMap - doit être enfant de MapContainer
const ClusterGroup = dynamic(
  () =>
    import('react-leaflet').then((mod) => {
      const { useMap } = mod
      return function ClusterGroup({ producers }: { producers: ProducerProfile[] }) {
        const map = useMap()
        const clusterGroupRef = useRef<any>(null)
        const markersRef = useRef<any[]>([])

        useEffect(() => {
          if (!map || producers.length === 0) return

          const setupClustering = async () => {
            const [{ default: L }, markercluster] = await Promise.all([
              import('leaflet'),
              import('leaflet.markercluster')
            ])

            const MC = (markercluster as any).default || markercluster

            // Créer le groupe de clustering
            if (!clusterGroupRef.current) {
              clusterGroupRef.current = new (MC as any).MarkerClusterGroup({
                maxClusterRadius: 50,
              })
              map.addLayer(clusterGroupRef.current)
            }

            // Nettoyer les anciens markers
            clusterGroupRef.current.clearLayers()
            markersRef.current.forEach(m => {
              if (m && m.remove) m.remove()
            })
            markersRef.current = []

            // Ajouter les nouveaux markers
            producers.forEach((producer) => {
              const marker = L.marker([parseFloat(producer.latitude), parseFloat(producer.longitude)])
              
              const popupContent = `
                <div style="padding: 8px;">
                  <h3 style="font-weight: bold; font-size: 18px; margin-bottom: 4px;">${producer.name}</h3>
                  <p style="font-size: 14px; color: #666; margin-bottom: 4px;">${producer.category}</p>
                  <p style="font-size: 12px; color: #999; margin-bottom: 8px;">${producer.address}</p>
                  <a href="/producers/${producer.id}" style="color: #22c55e; font-weight: 500; font-size: 14px;">Voir la fiche →</a>
                </div>
              `
              marker.bindPopup(popupContent)
              clusterGroupRef.current.addLayer(marker)
              markersRef.current.push(marker)
            })
          }

          setupClustering()

          return () => {
            if (clusterGroupRef.current && map) {
              map.removeLayer(clusterGroupRef.current)
              clusterGroupRef.current = null
            }
            markersRef.current.forEach(m => {
              if (m && m.remove) m.remove()
            })
            markersRef.current = []
          }
        }, [map, producers])

        return null
      }
    }),
  { ssr: false }
)

// La configuration Leaflet est faite dans layout.tsx

// Composant pour les markers simples (sans clustering si < 10)
function SimpleMarkers({ producers }: { producers: ProducerProfile[] }) {
  if (producers.length === 0) return null

  return (
    <>
      {producers.map((producer) => (
        <Marker
          key={producer.id}
          position={[parseFloat(producer.latitude), parseFloat(producer.longitude)]}
        >
          <Popup>
            <div className="p-2">
              <h3 className="font-bold text-lg mb-1">{producer.name}</h3>
              <p className="text-sm text-gray-600 mb-2">{producer.category}</p>
              <p className="text-xs text-gray-500 mb-2">{producer.address}</p>
              <a
                href={`/producers/${producer.id}`}
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                Voir la fiche →
              </a>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  )
}

interface MapViewProps {
  searchQuery?: string
  categoryFilter?: string
  distanceFilter?: number | null
  userLocation?: { lat: number; lng: number } | null
}

export function MapView({ searchQuery, categoryFilter, distanceFilter, userLocation }: MapViewProps = {}) {
  const [producers, setProducers] = useState<ProducerProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)
  const [center, setCenter] = useState<[number, number]>(MAP_DEFAULTS.center)
  const [zoom, setZoom] = useState<number>(MAP_DEFAULTS.zoom)

  useEffect(() => {
    // S'assurer qu'on est côté client
    if (typeof window !== 'undefined') {
      setMounted(true)
      loadProducers()
      
      // Géolocalisation
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setCenter([position.coords.latitude, position.coords.longitude])
            setZoom(MAP_DEFAULTS.zoomWithLocation)
          },
          () => {
            // Erreur de géolocalisation, on garde le centre par défaut
          }
        )
      }
    }
  }, [])

  const loadProducers = useCallback(async () => {
    try {
      setError(null)
      setLoading(true)
      let data
      
      // Si filtre par distance et position utilisateur disponible
      if (distanceFilter && userLocation) {
        data = await apiClient.getNearbyProducers(
          userLocation.lat,
          userLocation.lng,
          distanceFilter
        )
      } else {
        const params: Record<string, string> = {}
        if (categoryFilter) {
          params.category = categoryFilter
        }
        if (searchQuery) {
          params.search = searchQuery
        }
        data = await apiClient.getProducers(params)
      }
      
      setProducers(data.results || data)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors du chargement des producteurs'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [distanceFilter, userLocation, categoryFilter, searchQuery])

  useEffect(() => {
    // Recharger les producteurs quand les filtres changent
    if (mounted) {
      loadProducers()
    }
  }, [mounted, loadProducers])

  if (!mounted || loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-lg text-gray-600">Chargement de la carte...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50 p-4">
        <ErrorMessage message={error} onRetry={loadProducers} />
      </div>
    )
  }

  // Utiliser le clustering seulement si plus de 100 producteurs (selon spécification)
  const useClustering = producers.length > CLUSTERING_THRESHOLD

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height: '100%', width: '100%' }}
      className="z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {useClustering ? (
        <ClusterGroup producers={producers} />
      ) : (
        <SimpleMarkers producers={producers} />
      )}
    </MapContainer>
  )
}
