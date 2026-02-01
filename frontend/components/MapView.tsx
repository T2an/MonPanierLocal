'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { apiClient } from '@/lib/api'
import { MAP_DEFAULTS, CLUSTERING_THRESHOLD } from '@/lib/constants'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorMessage } from './ErrorMessage'
import { CATEGORY_COLORS } from './FilterSidebar'
import type { ProducerProfile } from '@/types'

// Import dynamique de tous les composants Leaflet pour éviter les erreurs SSR
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false })
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false })
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false })
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false })

// Fonction pour créer une icône SVG colorée selon la catégorie
function createColoredMarkerSvg(color: string): string {
  return `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="28" height="42">
      <defs>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="1" stdDeviation="1" flood-opacity="0.3"/>
        </filter>
      </defs>
      <path fill="${color}" stroke="#fff" stroke-width="1.5" filter="url(#shadow)"
        d="M12 0C5.4 0 0 5.4 0 12c0 7.2 12 24 12 24s12-16.8 12-24c0-6.6-5.4-12-12-12z"/>
      <circle cx="12" cy="12" r="5" fill="#fff"/>
    </svg>
  `
}

// Cache pour les icônes créées
const iconCache: Record<string, any> = {}

// Fonction pour obtenir/créer une icône colorée
async function getColoredIcon(L: any, category: string): Promise<any> {
  const colorData = CATEGORY_COLORS[category] || CATEGORY_COLORS['autre']
  const color = colorData.hex
  
  if (!iconCache[color]) {
    const svgString = createColoredMarkerSvg(color)
    const svgUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgString)}`
    
    iconCache[color] = L.icon({
      iconUrl: svgUrl,
      iconSize: [28, 42],
      iconAnchor: [14, 42],
      popupAnchor: [0, -42],
    })
  }
  
  return iconCache[color]
}

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

            // Ajouter les nouveaux markers avec icônes colorées
            for (const producer of producers) {
              const icon = await getColoredIcon(L, producer.category)
              const marker = L.marker(
                [parseFloat(producer.latitude), parseFloat(producer.longitude)],
                { icon }
              )
              
              const colorData = CATEGORY_COLORS[producer.category] || CATEGORY_COLORS['autre']
              const popupContent = `
                <div style="padding: 8px;">
                  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: ${colorData.hex};"></span>
                    <span style="font-size: 12px; color: ${colorData.hex}; font-weight: 600;">${producer.category}</span>
                  </div>
                  <h3 style="font-weight: bold; font-size: 18px; margin-bottom: 4px;">${producer.name}</h3>
                  <p style="font-size: 12px; color: #999; margin-bottom: 8px;">${producer.address}</p>
                  <a href="/producers/${producer.id}" style="color: ${colorData.hex}; font-weight: 500; font-size: 14px;">Voir la fiche →</a>
                </div>
              `
              marker.bindPopup(popupContent)
              clusterGroupRef.current.addLayer(marker)
              markersRef.current.push(marker)
            }
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

// Composant pour les markers simples avec icônes colorées
const SimpleMarkers = dynamic(
  () =>
    import('react-leaflet').then((mod) => {
      const { useMap } = mod
      return function SimpleMarkers({ producers }: { producers: ProducerProfile[] }) {
        const map = useMap()
        const markersRef = useRef<any[]>([])

        useEffect(() => {
          if (!map) return

          const setupMarkers = async () => {
            const { default: L } = await import('leaflet')

            // Nettoyer les anciens markers
            markersRef.current.forEach(m => {
              if (m && m.remove) m.remove()
            })
            markersRef.current = []

            // Ajouter les nouveaux markers avec icônes colorées
            for (const producer of producers) {
              const icon = await getColoredIcon(L, producer.category)
              const marker = L.marker(
                [parseFloat(producer.latitude), parseFloat(producer.longitude)],
                { icon }
              )
              
              const colorData = CATEGORY_COLORS[producer.category] || CATEGORY_COLORS['autre']
              const popupContent = `
                <div style="padding: 8px;">
                  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: ${colorData.hex};"></span>
                    <span style="font-size: 12px; color: ${colorData.hex}; font-weight: 600;">${producer.category}</span>
                  </div>
                  <h3 style="font-weight: bold; font-size: 18px; margin-bottom: 4px;">${producer.name}</h3>
                  <p style="font-size: 12px; color: #999; margin-bottom: 8px;">${producer.address}</p>
                  <a href="/producers/${producer.id}" style="color: ${colorData.hex}; font-weight: 500; font-size: 14px;">Voir la fiche →</a>
                </div>
              `
              marker.bindPopup(popupContent)
              marker.addTo(map)
              markersRef.current.push(marker)
            }
          }

          setupMarkers()

          return () => {
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

interface MapViewProps {
  categoryFilters?: string[]
  userLocation?: { lat: number; lng: number; name?: string } | null
  selectedProducer?: ProducerProfile | null
  locationSearchRadius?: number
}

export function MapView({ categoryFilters = [], userLocation, selectedProducer, locationSearchRadius = 20 }: MapViewProps = {}) {
  const [producers, setProducers] = useState<ProducerProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)
  const [center, setCenter] = useState<[number, number]>(MAP_DEFAULTS.center)
  const [zoom, setZoom] = useState<number>(MAP_DEFAULTS.zoom)
  const mapRef = useRef<any>(null)

  useEffect(() => {
    // S'assurer qu'on est côté client
    if (typeof window !== 'undefined') {
      setMounted(true)
    }
  }, [])

  // Gérer le zoom et le centre de la carte - mettre à jour le state pour le rendu initial
  useEffect(() => {
    if (!mounted) return

    if (userLocation) {
      // Zoom sur la ville sélectionnée
      setCenter([userLocation.lat, userLocation.lng])
      setZoom(12) // Zoom adapté pour voir une zone de 20km
    } else if (selectedProducer) {
      // Zoom sur le producteur sélectionné
      const lat = parseFloat(selectedProducer.latitude)
      const lng = parseFloat(selectedProducer.longitude)
      setCenter([lat, lng])
      setZoom(14) // Zoom plus proche pour un producteur unique
    } else {
      // Vue par défaut
      setCenter(MAP_DEFAULTS.center)
      setZoom(MAP_DEFAULTS.zoom)
    }
  }, [userLocation, selectedProducer, mounted])

  const loadProducers = useCallback(async () => {
    try {
      setError(null)
      setLoading(true)
      let data
      
      if (userLocation) {
        // Recherche par ville : 20km fixe autour de l'adresse
        data = await apiClient.getNearbyProducers(
          userLocation.lat,
          userLocation.lng,
          locationSearchRadius,
          categoryFilters.length > 0 ? categoryFilters : undefined
        )
      } else if (selectedProducer) {
        // Recherche par nom : afficher uniquement le producteur sélectionné
        setProducers([selectedProducer])
        setLoading(false)
        return
      } else {
        // Aucune recherche : afficher tous les producteurs
        data = await apiClient.getProducers({
          categories: categoryFilters.length > 0 ? categoryFilters : undefined
        })
      }
      
      let allProducers = data.results || data
      setProducers(allProducers)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors du chargement des producteurs'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [userLocation, selectedProducer, categoryFilters, locationSearchRadius])

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

  // Composant pour mettre à jour la référence de la carte et gérer le zoom dynamique
  const MapController = dynamic(
    () =>
      Promise.all([
        import('react-leaflet'),
        import('react')
      ]).then(([leafletMod, reactMod]) => {
        const { useMap } = leafletMod
        const { useEffect } = reactMod
        return function MapController({ 
          userLocation, 
          selectedProducer 
        }: { 
          userLocation?: { lat: number; lng: number; name?: string } | null
          selectedProducer?: ProducerProfile | null
        }) {
          const map = useMap()
          
          useEffect(() => {
            mapRef.current = map
          }, [map])

          // Mettre à jour le zoom quand userLocation ou selectedProducer change
          useEffect(() => {
            if (userLocation) {
              map.setView([userLocation.lat, userLocation.lng], 12)
            } else if (selectedProducer) {
              const lat = parseFloat(selectedProducer.latitude)
              const lng = parseFloat(selectedProducer.longitude)
              map.setView([lat, lng], 14)
            }
          }, [map, userLocation, selectedProducer])

          return null
        }
      }),
    { ssr: false }
  )

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height: '100%', width: '100%' }}
      className="z-0"
    >
      <MapController userLocation={userLocation} selectedProducer={selectedProducer} />
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
