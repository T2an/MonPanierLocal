'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { MAP_DEFAULTS } from '@/lib/constants'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorMessage } from '@/components/ErrorMessage'
import { PhotoManager } from '@/components/PhotoManager'
import { ProductManager } from '@/components/ProductManager'
import { SaleModeManager } from '@/components/SaleModeManager'
import { ProductCalendar } from '@/components/ProductCalendar'
import { ToastContainer, type ToastType } from '@/components/Toast'
import { PRODUCER_CATEGORIES } from '@/lib/constants'
import type { ProducerProfile, Product } from '@/types'
import dynamic from 'next/dynamic'

const MapContainer = dynamic(() => import('react-leaflet').then((mod) => mod.MapContainer), { ssr: false })
const TileLayer = dynamic(() => import('react-leaflet').then((mod) => mod.TileLayer), { ssr: false })
const Marker = dynamic(() => import('react-leaflet').then((mod) => mod.Marker), { ssr: false })

// Composant pour gérer les clics sur la carte
function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  const MapEvents = dynamic(
    () => import('react-leaflet').then((mod) => {
      const { useMapEvents } = mod
      return function MapClickHandlerInner({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
        useMapEvents({
          click: (e) => onMapClick(e.latlng.lat, e.latlng.lng),
        })
        return null
      }
    }),
    { ssr: false }
  )
  return <MapEvents onMapClick={onMapClick} />
}

type TabId = 'info' | 'location' | 'products' | 'sales' | 'contact'

const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: 'info', label: 'Mon exploitation', icon: '🏠' },
  { id: 'location', label: 'Localisation', icon: '📍' },
  { id: 'products', label: 'Produits', icon: '📦' },
  { id: 'sales', label: 'Points de vente', icon: '🛒' },
  { id: 'contact', label: 'Contact', icon: '📞' },
]

export default function ProducerEditPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [producer, setProducer] = useState<ProducerProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [activeTab, setActiveTab] = useState<TabId>('info')
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'autre' as ProducerProfile['category'],
    address: '',
    latitude: '',
    longitude: '',
    phone: '',
    email_contact: '',
    website: '',
    opening_hours: '',
  })
  const [products, setProducts] = useState<Product[]>([])
  const [mapCenter, setMapCenter] = useState<[number, number]>(MAP_DEFAULTS.center)
  const [mapZoom, setMapZoom] = useState<number>(MAP_DEFAULTS.zoom)
  const [error, setError] = useState<string | null>(null)
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type?: ToastType }>>([])
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastSavedFormDataRef = useRef<string>('')
  
  // État pour la recherche d'adresse
  const [addressSearch, setAddressSearch] = useState('')
  const [addressSuggestions, setAddressSuggestions] = useState<any[]>([])
  const [isSearchingAddress, setIsSearchingAddress] = useState(false)
  const [isAddressInputFocused, setIsAddressInputFocused] = useState(false)
  const [userHasTyped, setUserHasTyped] = useState(false)
  const addressSearchTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!authLoading && (!user || !user.is_producer)) {
      router.push('/profile')
      return
    }
    loadProducer()
  }, [user, authLoading])

  const loadProducer = async () => {
    try {
      const producers = await apiClient.getProducers()
      const userProducer = producers.results.find((p) => p.user.id === user?.id)
      if (userProducer) {
        setProducer(userProducer)
        const newFormData = {
          name: userProducer.name,
          description: userProducer.description || '',
          category: userProducer.category,
          address: userProducer.address,
          latitude: userProducer.latitude,
          longitude: userProducer.longitude,
          phone: userProducer.phone || '',
          email_contact: userProducer.email_contact || '',
          website: userProducer.website || '',
          opening_hours: userProducer.opening_hours || '',
        }
        setFormData(newFormData)
        setAddressSearch(userProducer.address)
        lastSavedFormDataRef.current = JSON.stringify(newFormData)
        setMapCenter([parseFloat(userProducer.latitude), parseFloat(userProducer.longitude)])
        setMapZoom(MAP_DEFAULTS.zoomWithLocation)
        setProducts(userProducer.products || [])
      }
    } catch (err) {
      setError('Erreur lors du chargement du producteur')
    } finally {
      setLoading(false)
    }
  }

  const addToast = useCallback((message: string, type: ToastType = 'success') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    return id
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  // Recherche d'adresse avec Nominatim
  const searchAddress = async (query: string) => {
    if (query.length < 3) {
      setAddressSuggestions([])
      return
    }
    setIsSearchingAddress(true)
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5&countrycodes=fr&addressdetails=1`,
        { headers: { 'User-Agent': 'MonPanierLocal/1.0' } }
      )
      const data = await response.json()
      setAddressSuggestions(data)
    } catch (err) {
      console.error('Erreur recherche adresse:', err)
    } finally {
      setIsSearchingAddress(false)
    }
  }

  // Debounce pour la recherche d'adresse - seulement si l'utilisateur a tapé et le champ est focus
  useEffect(() => {
    if (!userHasTyped || !isAddressInputFocused) {
      setAddressSuggestions([])
      return
    }
    if (addressSearchTimeoutRef.current) clearTimeout(addressSearchTimeoutRef.current)
    addressSearchTimeoutRef.current = setTimeout(() => {
      searchAddress(addressSearch)
    }, 300)
    return () => {
      if (addressSearchTimeoutRef.current) clearTimeout(addressSearchTimeoutRef.current)
    }
  }, [addressSearch, userHasTyped, isAddressInputFocused])
  
  // Reverse geocoding: obtenir l'adresse à partir des coordonnées
  const reverseGeocode = async (lat: number, lng: number) => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&addressdetails=1`,
        { headers: { 'User-Agent': 'MonPanierLocal/1.0' } }
      )
      const data = await response.json()
      if (data && data.display_name) {
        return data.display_name
      }
    } catch (err) {
      console.error('Erreur reverse geocoding:', err)
    }
    return null
  }

  const handleSelectAddress = (suggestion: any) => {
    const lat = parseFloat(suggestion.lat)
    const lng = parseFloat(suggestion.lon)
    setFormData({
      ...formData,
      address: suggestion.display_name,
      latitude: lat.toString(),
      longitude: lng.toString(),
    })
    setAddressSearch(suggestion.display_name)
    setAddressSuggestions([])
    setUserHasTyped(false)
    setIsAddressInputFocused(false)
    setMapCenter([lat, lng])
    setMapZoom(15)
  }

  const saveFormData = useCallback(async (showToast = true) => {
    if (!formData.name.trim()) {
      if (showToast) addToast('Veuillez renseigner le nom de l\'exploitation', 'error')
      setSaveStatus('error')
      return
    }
    if (!formData.address.trim()) {
      if (showToast) addToast('Veuillez renseigner l\'adresse', 'error')
      setSaveStatus('error')
      return
    }
    if (!formData.latitude || !formData.longitude) {
      if (showToast) addToast('Veuillez définir la position (recherchez une adresse ou cliquez sur la carte)', 'error')
      setSaveStatus('error')
      return
    }

    if (!producer) {
      try {
        setSaveStatus('saving')
        const newProducer = await apiClient.createProducer(formData)
        setProducer(newProducer)
        lastSavedFormDataRef.current = JSON.stringify(formData)
        setSaveStatus('saved')
        if (showToast) addToast('Exploitation créée avec succès !', 'success')
        await loadProducer()
      } catch (err) {
        setSaveStatus('error')
        if (showToast) addToast(err instanceof Error ? err.message : 'Erreur lors de la création', 'error')
      }
      return
    }

    const currentFormDataStr = JSON.stringify(formData)
    if (currentFormDataStr === lastSavedFormDataRef.current) return

    try {
      setSaveStatus('saving')
      await apiClient.updateProducer(producer.id, formData)
      lastSavedFormDataRef.current = currentFormDataStr
      setSaveStatus('saved')
      if (showToast) addToast('Modifications enregistrées', 'success')
      setTimeout(() => setSaveStatus('idle'), 2000)
    } catch (err) {
      setSaveStatus('error')
      if (showToast) addToast(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde', 'error')
    }
  }, [producer, formData, addToast])

  useEffect(() => {
    if (!producer || loading) return
    if (autoSaveTimeoutRef.current) clearTimeout(autoSaveTimeoutRef.current)
    autoSaveTimeoutRef.current = setTimeout(() => saveFormData(false), 2000)
    return () => { if (autoSaveTimeoutRef.current) clearTimeout(autoSaveTimeoutRef.current) }
  }, [formData, producer, loading, saveFormData])

  const handleMapClick = async (lat: number, lng: number) => {
    // Mise à jour immédiate des coordonnées
    setFormData(prev => ({ ...prev, latitude: lat.toString(), longitude: lng.toString() }))
    setMapCenter([lat, lng])
    
    // Reverse geocoding pour obtenir l'adresse
    const address = await reverseGeocode(lat, lng)
    if (address) {
      setFormData(prev => ({ 
        ...prev, 
        address: address,
        latitude: lat.toString(), 
        longitude: lng.toString() 
      }))
      setAddressSearch(address)
      setUserHasTyped(false)
      addToast('Position et adresse mises à jour', 'success')
    } else {
      // Si le reverse geocoding échoue, mettre une adresse générique
      const genericAddress = `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`
      setFormData(prev => ({ 
        ...prev, 
        address: genericAddress,
        latitude: lat.toString(), 
        longitude: lng.toString() 
      }))
      setAddressSearch(genericAddress)
    }
  }

  const handleUseMyLocation = () => {
    if (typeof window !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude
          const lng = position.coords.longitude
          setFormData(prev => ({ ...prev, latitude: lat.toString(), longitude: lng.toString() }))
          setMapCenter([lat, lng])
          setMapZoom(15)
          
          // Reverse geocoding pour obtenir l'adresse
          const address = await reverseGeocode(lat, lng)
          if (address) {
            setFormData(prev => ({ 
              ...prev, 
              address: address,
              latitude: lat.toString(), 
              longitude: lng.toString() 
            }))
            setAddressSearch(address)
            setUserHasTyped(false)
            addToast('Position GPS et adresse mises à jour', 'success')
          }
        },
        () => addToast('Impossible d\'obtenir votre position.', 'error')
      )
    }
  }

  const handlePhotoUpload = async (file: File) => {
    if (!producer) return
    try {
      await apiClient.uploadPhoto(producer.id, file)
      addToast('Photo ajoutée', 'success')
      await loadProducer()
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'Erreur', 'error')
    }
  }

  const handleDeletePhoto = async (photoId: number) => {
    try {
      await apiClient.deletePhoto(photoId)
      addToast('Photo supprimée', 'success')
      await loadProducer()
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'Erreur', 'error')
    }
  }

  const handleCreateProduct = async (data: any) => {
    if (!producer) return
    try {
      await apiClient.createProduct(producer.id, data)
      addToast('Produit ajouté', 'success')
      await loadProducer()
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'Erreur', 'error')
    }
  }

  const handleDeleteProduct = async (productId: number) => {
    try {
      await apiClient.deleteProduct(productId)
      addToast('Produit supprimé', 'success')
      await loadProducer()
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'Erreur', 'error')
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const inputClass = "w-full px-4 py-3 border-2 border-nature-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b-4 border-nature-200 rounded-b-2xl shadow-lg mb-6 -mx-4 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-nature-800">
            {producer ? '🌾 Mon exploitation' : '🌱 Créer mon exploitation'}
          </h1>
          <div className="flex items-center gap-3">
            {saveStatus === 'saving' && <span className="text-sm text-nature-600 flex items-center gap-2"><LoadingSpinner size="sm" /> Sauvegarde...</span>}
            {saveStatus === 'saved' && <span className="text-sm text-nature-600">✓ Sauvegardé</span>}
            {saveStatus === 'error' && <span className="text-sm text-red-600">✕ Erreur</span>}
            <button
              onClick={() => saveFormData(true)}
              disabled={saveStatus === 'saving'}
              className="px-5 py-2 bg-nature-500 hover:bg-nature-600 text-white rounded-xl font-semibold disabled:opacity-50 transition-all"
            >
              💾 Enregistrer
            </button>
          </div>
        </div>
      </div>

      {error && <ErrorMessage message={error} className="mb-6" />}

      {/* Navigation par onglets */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            disabled={!producer && tab.id !== 'info' && tab.id !== 'location'}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-nature-500 text-white shadow-lg'
                : 'bg-white text-earth-700 hover:bg-nature-50 border-2 border-nature-200'
            } ${!producer && tab.id !== 'info' && tab.id !== 'location' ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Contenu des onglets */}
      <div className="bg-white rounded-2xl shadow-lg border-2 border-nature-200 p-6">
        
        {/* Onglet: Mon exploitation */}
        {activeTab === 'info' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-nature-800 flex items-center gap-2">
              <span>🏠</span> Informations générales
            </h2>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nom de l'exploitation *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className={inputClass}
                placeholder="Ex: Ferme du Soleil"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className={inputClass}
                placeholder="Présentez votre exploitation..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Activité principale *</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value as ProducerProfile['category'] })}
                className={inputClass}
              >
                {PRODUCER_CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>

            {producer && (
              <div className="pt-4 border-t-2 border-nature-100">
                <h3 className="text-lg font-semibold text-nature-800 mb-4">📷 Photos de l'exploitation</h3>
                <PhotoManager
                  photos={producer.photos || []}
                  onUpload={handlePhotoUpload}
                  onDelete={handleDeletePhoto}
                />
              </div>
            )}
          </div>
        )}

        {/* Onglet: Localisation */}
        {activeTab === 'location' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-nature-800 flex items-center gap-2">
              <span>📍</span> Localisation de l'exploitation
            </h2>

            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">Rechercher une adresse *</label>
              <div className="relative">
                <input
                  type="text"
                  value={addressSearch}
                  onChange={(e) => {
                    setAddressSearch(e.target.value)
                    setUserHasTyped(true)
                  }}
                  onFocus={() => setIsAddressInputFocused(true)}
                  onBlur={() => {
                    // Délai pour permettre le clic sur une suggestion
                    setTimeout(() => {
                      setIsAddressInputFocused(false)
                      setAddressSuggestions([])
                    }, 200)
                  }}
                  className={`${inputClass} pr-10`}
                  placeholder="Tapez une adresse, ville ou code postal..."
                />
                {isSearchingAddress && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <LoadingSpinner size="sm" />
                  </div>
                )}
              </div>
              
              {addressSuggestions.length > 0 && isAddressInputFocused && (
                <div className="absolute z-50 w-full mt-1 bg-white border-2 border-nature-300 rounded-xl shadow-xl max-h-60 overflow-y-auto">
                  {addressSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => handleSelectAddress(suggestion)}
                      className="w-full text-left px-4 py-3 hover:bg-nature-50 border-b border-nature-100 last:border-b-0 text-sm"
                    >
                      📍 {suggestion.display_name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleUseMyLocation}
                className="px-4 py-2 bg-nature-100 hover:bg-nature-200 text-nature-700 rounded-xl font-medium transition-all flex items-center gap-2"
              >
                🎯 Utiliser ma position GPS
              </button>
            </div>

            {(!formData.latitude || !formData.longitude) && (
              <div className="p-4 bg-amber-50 border-2 border-amber-300 rounded-xl">
                <p className="text-amber-800 text-sm font-medium">
                  ⚠️ Position non définie - Recherchez une adresse ou cliquez sur la carte
                </p>
              </div>
            )}

            <div className={`h-80 rounded-xl overflow-hidden border-4 ${formData.latitude && formData.longitude ? 'border-nature-300' : 'border-amber-400'}`}>
              <MapContainer center={mapCenter} zoom={mapZoom} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                  attribution='&copy; OpenStreetMap'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapClickHandler onMapClick={handleMapClick} />
                {formData.latitude && formData.longitude && (
                  <Marker position={[parseFloat(formData.latitude), parseFloat(formData.longitude)]} />
                )}
              </MapContainer>
            </div>

            {formData.latitude && formData.longitude && (
              <p className="text-sm text-nature-600">
                ✓ Position : {parseFloat(formData.latitude).toFixed(5)}, {parseFloat(formData.longitude).toFixed(5)}
              </p>
            )}
          </div>
        )}

        {/* Onglet: Produits */}
        {activeTab === 'products' && producer && (
          <div className="space-y-8">
            {/* Calendrier de disponibilité */}
            <div>
              <h2 className="text-xl font-bold text-nature-800 flex items-center gap-2 mb-4">
                <span>📅</span> Calendrier de disponibilité
              </h2>
              <ProductCalendar products={products} />
            </div>

            {/* Gestion des produits */}
            <div className="pt-6 border-t-2 border-nature-200">
              <h2 className="text-xl font-bold text-nature-800 flex items-center gap-2 mb-2">
                <span>📦</span> Gérer mes produits
              </h2>
              <p className="text-gray-600 mb-4">Ajoutez, modifiez ou supprimez vos produits et définissez leur période de disponibilité.</p>
              <ProductManager
                products={products}
                onCreate={handleCreateProduct}
                onUpdate={() => loadProducer()}
                onDelete={handleDeleteProduct}
                onRefresh={loadProducer}
              />
            </div>
          </div>
        )}

        {/* Onglet: Points de vente */}
        {activeTab === 'sales' && producer && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-nature-800 flex items-center gap-2">
              <span>🛒</span> Points de vente
            </h2>
            <p className="text-gray-600">Indiquez comment les clients peuvent acheter vos produits.</p>
            <SaleModeManager producer={producer} onRefresh={loadProducer} />
          </div>
        )}

        {/* Onglet: Contact */}
        {activeTab === 'contact' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-nature-800 flex items-center gap-2">
              <span>📞</span> Informations de contact
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className={inputClass}
                  placeholder="06 12 34 56 78"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email de contact</label>
                <input
                  type="email"
                  value={formData.email_contact}
                  onChange={(e) => setFormData({ ...formData, email_contact: e.target.value })}
                  className={inputClass}
                  placeholder="contact@ferme.fr"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Site web</label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                className={inputClass}
                placeholder="https://www.maferme.fr"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Horaires d'ouverture</label>
              <textarea
                value={formData.opening_hours}
                onChange={(e) => setFormData({ ...formData, opening_hours: e.target.value })}
                rows={4}
                className={inputClass}
                placeholder="Lundi - Vendredi : 9h - 18h&#10;Samedi : 9h - 12h&#10;Dimanche : Fermé"
              />
            </div>
          </div>
        )}
      </div>

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  )
}
