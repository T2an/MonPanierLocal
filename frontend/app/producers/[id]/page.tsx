'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorMessage } from '@/components/ErrorMessage'
import { getImageUrl } from '@/lib/imageUrl'
import { ProductCard } from '@/components/ProductCard'
import { OpeningStatusBadge } from '@/components/OpeningStatusBadge'
import { WeeklySchedule, SingleModeSchedule } from '@/components/WeeklySchedule'
import type { ProducerProfile, SaleMode } from '@/types'
import Link from 'next/link'
import dynamic from 'next/dynamic'

// Import dynamique pour la carte
const MapContainer = dynamic(() => import('react-leaflet').then((mod) => mod.MapContainer), {
  ssr: false,
})
const TileLayer = dynamic(() => import('react-leaflet').then((mod) => mod.TileLayer), {
  ssr: false,
})
const Marker = dynamic(() => import('react-leaflet').then((mod) => mod.Marker), {
  ssr: false,
})

const DAYS_OF_WEEK = [
  { value: 0, label: 'Lundi' },
  { value: 1, label: 'Mardi' },
  { value: 2, label: 'Mercredi' },
  { value: 3, label: 'Jeudi' },
  { value: 4, label: 'Vendredi' },
  { value: 5, label: 'Samedi' },
  { value: 6, label: 'Dimanche' },
]

export default function ProducerDetailPage() {
  const params = useParams()
  const id = parseInt(params.id as string)
  const [producer, setProducer] = useState<ProducerProfile | null>(null)
  const [saleModes, setSaleModes] = useState<SaleMode[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadProducer()
    loadSaleModes()
  }, [id])

  const loadProducer = async () => {
    try {
      setError(null)
      const data = await apiClient.getProducer(id)
      setProducer(data)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors du chargement du producteur'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const loadSaleModes = async () => {
    try {
      const modes = await apiClient.getSaleModes(id)
      setSaleModes(modes)
    } catch (err) {
      console.error('Error loading sale modes:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-lg text-gray-600">Chargement...</p>
        </div>
      </div>
    )
  }

  if (error || !producer) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <ErrorMessage
          message={error || 'Producteur non trouvé'}
          onRetry={error ? loadProducer : undefined}
        />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link
        href="/"
              className="text-nature-600 hover:text-nature-700 mb-6 inline-block font-semibold text-lg flex items-center gap-2"
      >
        ← Retour à la carte
      </Link>

      <div className="bg-white rounded-3xl shadow-nature-lg overflow-hidden border-4 border-nature-200">
        {producer.photos && producer.photos.length > 0 && (
          <div className="relative h-64 md:h-96">
            <img
              src={getImageUrl(producer.photos[0].image_file)}
              alt={producer.name}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{producer.name}</h1>
              <span className="inline-block bg-nature-200 text-nature-800 text-sm font-bold px-4 py-2 rounded-2xl border-2 border-nature-300">
                {producer.category}
              </span>
            </div>
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Description</h2>
            <p className="text-gray-700">{producer.description || 'Aucune description disponible.'}</p>
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Adresse</h2>
            <p className="text-gray-700 mb-4">{producer.address}</p>
            
            {/* Carte intégrée */}
            <div className="h-64 rounded-lg overflow-hidden border border-gray-300">
              <MapContainer
                center={[parseFloat(producer.latitude), parseFloat(producer.longitude)]}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={false}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker position={[parseFloat(producer.latitude), parseFloat(producer.longitude)]} />
              </MapContainer>
            </div>
            
            {/* Bouton directions */}
            <div className="mt-4">
              <a
                href={`https://www.google.com/maps/dir/?api=1&destination=${producer.latitude},${producer.longitude}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl font-semibold shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105"
              >
                <span>🧭</span>
                Itinéraire
              </a>
            </div>
          </div>

          {/* Contact */}
          {(producer.phone || producer.email_contact || producer.website) && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Contact</h2>
              <div className="space-y-2">
                {producer.phone && (
                  <div className="flex items-center gap-2">
                    <span className="text-lg">📞</span>
                    <a
                      href={`tel:${producer.phone}`}
                      className="text-nature-600 hover:text-nature-700 font-medium"
                    >
                      {producer.phone}
                    </a>
                  </div>
                )}
                {producer.email_contact && (
                  <div className="flex items-center gap-2">
                    <span className="text-lg">✉️</span>
                    <a
                      href={`mailto:${producer.email_contact}`}
                      className="text-nature-600 hover:text-nature-700 font-medium"
                    >
                      {producer.email_contact}
                    </a>
                  </div>
                )}
                {producer.website && (
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🌐</span>
                    <a
                      href={producer.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-nature-600 hover:text-nature-700 font-medium"
                    >
                      {producer.website}
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Horaires généraux */}
          {producer.opening_hours && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Horaires d'ouverture</h2>
              <p className="text-gray-700 whitespace-pre-line">{producer.opening_hours}</p>
            </div>
          )}

          {/* Semainier global des disponibilités */}
          {saleModes.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-4">📅 Disponibilités de la semaine</h2>
              <WeeklySchedule saleModes={saleModes} />
            </div>
          )}

          {/* Modes de vente */}
          {saleModes.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-4">Modes de vente</h2>
              <div className="space-y-4">
                {saleModes.map((mode) => (
                  <div
                    key={mode.id}
                    className="bg-gradient-to-br from-nature-50 to-white p-6 rounded-3xl border-4 border-nature-200 shadow-nature"
                  >
                    <div className="flex items-start gap-3 mb-3">
                      <div className="text-3xl">
                        {mode.mode_type === 'on_site' && '🏪'}
                        {mode.mode_type === 'phone_order' && '📞'}
                        {mode.mode_type === 'vending_machine' && '🤖'}
                        {mode.mode_type === 'delivery' && '🚚'}
                        {mode.mode_type === 'market' && '🏪'}
                      </div>
                      <div className="flex-1">
                        <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                          <div>
                            <h3 className="text-lg font-bold text-nature-800">{mode.title}</h3>
                            <p className="text-sm text-nature-600 font-medium">
                              {mode.mode_type_display || mode.mode_type}
                            </p>
                          </div>
                          {/* Badge de statut d'ouverture */}
                          <OpeningStatusBadge 
                            openingHours={mode.opening_hours} 
                            is24_7={mode.is_24_7}
                          />
                        </div>
                        {mode.instructions && (
                          <p className="text-gray-700 mb-3 bg-white p-3 rounded-xl border-2 border-nature-200">
                            <strong className="text-nature-700">Consigne :</strong> {mode.instructions}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="space-y-2 ml-12">
                      {/* Informations spécifiques selon le type */}
                      {mode.phone_number && (
                        <div className="flex items-center gap-2 text-gray-700">
                          <span className="text-lg">📞</span>
                          <a
                            href={`tel:${mode.phone_number}`}
                            className="text-nature-600 hover:text-nature-700 font-medium"
                          >
                            {mode.phone_number}
                          </a>
                        </div>
                      )}

                      {mode.website_url && (
                        <div className="flex items-center gap-2 text-gray-700">
                          <span className="text-lg">🌐</span>
                          <a
                            href={mode.website_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-nature-600 hover:text-nature-700 font-medium"
                          >
                            {mode.website_url}
                          </a>
                        </div>
                      )}

                      {mode.location_address && (
                        <div className="flex items-start gap-2 text-gray-700">
                          <span className="text-lg">📍</span>
                          <span>{mode.location_address}</span>
                        </div>
                      )}

                      {mode.is_24_7 && (
                        <div className="flex items-center gap-2 text-nature-600 font-semibold">
                          <span className="text-lg">🕐</span>
                          <span>Disponible 24/7</span>
                        </div>
                      )}

                      {mode.market_info && (
                        <div className="flex items-start gap-2 text-gray-700 bg-white p-3 rounded-xl border-2 border-nature-200">
                          <span className="text-lg">📋</span>
                          <span className="whitespace-pre-line">{mode.market_info}</span>
                        </div>
                      )}

                      {/* Semainier visuel */}
                      {(mode.opening_hours && mode.opening_hours.length > 0) || mode.is_24_7 ? (
                        <div className="mt-3 bg-white p-4 rounded-xl border-2 border-nature-200">
                          <p className="text-sm font-semibold text-nature-700 mb-3">Disponibilités :</p>
                          <SingleModeSchedule 
                            openingHours={mode.opening_hours} 
                            is24_7={mode.is_24_7} 
                          />
                        </div>
                      ) : null}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {producer.photos && producer.photos.length > 1 && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-4">Photos</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {producer.photos.slice(1).map((photo) => (
                  <div key={photo.id} className="relative h-48 rounded-lg overflow-hidden">
                    <img
                      src={getImageUrl(photo.image_file)}
                      alt={producer.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-8 pt-6 border-t">
            <h2 className="text-xl font-semibold mb-4">Produits</h2>
            {producer.products && producer.products.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {producer.products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            ) : (
              <p className="text-gray-500">Aucun produit renseigné pour le moment.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

