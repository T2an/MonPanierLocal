'use client'

import { useEffect } from 'react'
import { PRODUCER_CATEGORIES } from '@/lib/constants'
import type { ProducerProfile } from '@/types'
import dynamic from 'next/dynamic'
// La configuration Leaflet est faite dans layout.tsx

const MapContainer = dynamic(() => import('react-leaflet').then((mod) => mod.MapContainer), {
  ssr: false,
})
const TileLayer = dynamic(() => import('react-leaflet').then((mod) => mod.TileLayer), {
  ssr: false,
})
const Marker = dynamic(() => import('react-leaflet').then((mod) => mod.Marker), {
  ssr: false,
})

// Composant pour gérer les clics sur la carte
function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  const MapEvents = dynamic(
    () =>
      import('react-leaflet').then((mod) => {
        const { useMapEvents } = mod
        return function MapClickHandlerInner({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
          useMapEvents({
            click: (e) => {
              onMapClick(e.latlng.lat, e.latlng.lng)
            },
          })
          return null
        }
      }),
    { ssr: false }
  )
  return <MapEvents onMapClick={onMapClick} />
}

interface ProducerFormData {
  name: string
  description: string
  category: ProducerProfile['category']
  address: string
  latitude: string
  longitude: string
  phone: string
  email_contact: string
  website: string
  opening_hours: string
}

interface ProducerFormProps {
  formData: ProducerFormData
  onFormDataChange: (data: Partial<ProducerFormData>) => void
  mapCenter: [number, number]
  mapZoom: number
  onMapClick: (lat: number, lng: number) => void
  onUseMyLocation: () => void
}

export function ProducerForm({
  formData,
  onFormDataChange,
  mapCenter,
  mapZoom,
  onMapClick,
  onUseMyLocation,
}: ProducerFormProps) {
  return (
    <div className="bg-white rounded-3xl shadow-nature-lg p-8 space-y-6 border-4 border-nature-200">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nom de l'exploitation *
        </label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => onFormDataChange({ name: e.target.value })}
          className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => onFormDataChange({ description: e.target.value })}
          rows={4}
          className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Activité principale de votre exploitation *</label>
        <select
          required
          value={formData.category}
          onChange={(e) =>
            onFormDataChange({ category: e.target.value as ProducerProfile['category'] })
          }
          className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
        >
          {PRODUCER_CATEGORIES.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Adresse *</label>
        <input
          type="text"
          required
          value={formData.address}
          onChange={(e) => onFormDataChange({ address: e.target.value })}
          className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => onFormDataChange({ phone: e.target.value })}
          placeholder="06 12 34 56 78"
          className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Email de contact</label>
        <input
          type="email"
          value={formData.email_contact}
          onChange={(e) => onFormDataChange({ email_contact: e.target.value })}
          placeholder="contact@example.com"
          className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Site web</label>
        <input
          type="url"
          value={formData.website}
          onChange={(e) => onFormDataChange({ website: e.target.value })}
          placeholder="https://example.com"
          className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Horaires d'ouverture</label>
        <textarea
          value={formData.opening_hours}
          onChange={(e) => onFormDataChange({ opening_hours: e.target.value })}
          rows={3}
          placeholder="Lundi - Vendredi: 9h - 18h&#10;Samedi: 9h - 12h"
          className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Position sur la carte *
        </label>
        {(!formData.latitude || !formData.longitude) && (
          <div className="mb-3 p-3 bg-amber-50 border-2 border-amber-300 rounded-2xl">
            <p className="text-amber-800 text-sm font-medium">
              ⚠️ Position non définie - Cliquez sur la carte ou utilisez le bouton ci-dessous
            </p>
          </div>
        )}
        <div className="flex gap-2 mb-2">
          <button
            type="button"
            onClick={onUseMyLocation}
            className="px-5 py-2.5 bg-nature-500 hover:bg-nature-600 text-white text-sm font-semibold rounded-2xl shadow-nature transition-all transform hover:scale-105"
          >
            📍 Utiliser ma position
          </button>
        </div>
        <div className={`h-64 rounded-2xl overflow-hidden border-4 shadow-nature ${formData.latitude && formData.longitude ? 'border-nature-300' : 'border-amber-400'}`}>
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapClickHandler onMapClick={onMapClick} />
            {formData.latitude && formData.longitude && (
              <Marker position={[parseFloat(formData.latitude), parseFloat(formData.longitude)]} />
            )}
          </MapContainer>
        </div>
        <p className={`mt-2 text-sm ${formData.latitude && formData.longitude ? 'text-nature-600' : 'text-amber-600'}`}>
          {formData.latitude && formData.longitude ? (
            <>✓ Position définie : {parseFloat(formData.latitude).toFixed(5)}, {parseFloat(formData.longitude).toFixed(5)}</>
          ) : (
            <>Cliquez sur la carte pour définir l'emplacement de votre exploitation</>
          )}
        </p>
      </div>
    </div>
  )
}
