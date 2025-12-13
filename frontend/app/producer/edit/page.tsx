'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { MAP_DEFAULTS } from '@/lib/constants'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorMessage } from '@/components/ErrorMessage'
import { ProducerForm } from '@/components/ProducerForm'
import { PhotoManager } from '@/components/PhotoManager'
import { ProductManager } from '@/components/ProductManager'
import { SaleModeManager } from '@/components/SaleModeManager'
import { ToastContainer, type ToastType } from '@/components/Toast'
import type { ProducerProfile, Product } from '@/types'

export default function ProducerEditPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [producer, setProducer] = useState<ProducerProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
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
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type?: ToastType; action?: { label: string; onClick: () => void } }>>([])
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastSavedFormDataRef = useRef<string>('')

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
        lastSavedFormDataRef.current = JSON.stringify(newFormData)
        setMapCenter([parseFloat(userProducer.latitude), parseFloat(userProducer.longitude)])
        setMapZoom(MAP_DEFAULTS.zoomWithLocation)
        setProducts(userProducer.products || [])
      }
    } catch (err: unknown) {
      setError('Erreur lors du chargement du producteur')
    } finally {
      setLoading(false)
    }
  }

  // Fonction pour ajouter un toast
  const addToast = useCallback((message: string, type: ToastType = 'success', action?: { label: string; onClick: () => void }) => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type, action }])
    return id
  }, [])

  // Fonction pour supprimer un toast
  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  // Fonction de sauvegarde du formulaire principal
  const saveFormData = useCallback(async (showToast = true) => {
    if (!producer) {
      // Si pas de producteur, on crée
      try {
        setSaveStatus('saving')
        const newProducer = await apiClient.createProducer(formData)
        setProducer(newProducer)
        lastSavedFormDataRef.current = JSON.stringify(formData)
        setSaveStatus('saved')
        if (showToast) {
          addToast('Exploitation créée avec succès !', 'success')
        }
        await loadProducer()
      } catch (err: unknown) {
        setSaveStatus('error')
        const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la création'
        if (showToast) {
          addToast(errorMessage, 'error')
        }
        throw err
      }
      return
    }

    // Vérifier si les données ont changé
    const currentFormDataStr = JSON.stringify(formData)
    if (currentFormDataStr === lastSavedFormDataRef.current) {
      return // Pas de changement
    }

    try {
      setSaveStatus('saving')
      await apiClient.updateProducer(producer.id, formData)
      lastSavedFormDataRef.current = currentFormDataStr
      setSaveStatus('saved')
      if (showToast) {
        addToast('Modifications enregistrées', 'success')
      }
      // Réinitialiser le statut après 2 secondes
      setTimeout(() => setSaveStatus('idle'), 2000)
    } catch (err: unknown) {
      setSaveStatus('error')
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la sauvegarde'
      if (showToast) {
        addToast(errorMessage, 'error')
      }
      throw err
    }
  }, [producer, formData, addToast])

  // Sauvegarde automatique avec debounce pour le formulaire
  useEffect(() => {
    if (!producer || loading) return

    // Annuler le timeout précédent
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current)
    }

    // Démarrer un nouveau timeout (2 secondes après la dernière modification)
    autoSaveTimeoutRef.current = setTimeout(() => {
      saveFormData(false) // Sauvegarde silencieuse
    }, 2000)

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current)
      }
    }
  }, [formData, producer, loading, saveFormData])

  const handleMapClick = (lat: number, lng: number) => {
    setFormData({
      ...formData,
      latitude: lat.toString(),
      longitude: lng.toString(),
    })
    setMapCenter([lat, lng])
  }

  const handleUseMyLocation = () => {
    if (typeof window !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude
          const lng = position.coords.longitude
          setFormData({
            ...formData,
            latitude: lat.toString(),
            longitude: lng.toString(),
          })
          setMapCenter([lat, lng])
          setMapZoom(15)
        },
        () => {
          alert('Impossible d\'obtenir votre position. Veuillez placer le marqueur manuellement.')
        }
      )
    }
  }

  const handleManualSave = async () => {
    try {
      setError(null)
      await saveFormData(true)
    } catch (err: unknown) {
      let errorMessage = 'Erreur lors de la sauvegarde'
      if (err instanceof Error) {
        errorMessage = err.message
      } else if (typeof err === 'object' && err !== null && 'response' in err) {
        const axiosError = err as { response?: { data?: { error?: string } } }
        errorMessage = axiosError.response?.data?.error || errorMessage
      }
      setError(errorMessage)
    }
  }

  const handlePhotoUpload = async (file: File) => {
    if (!producer) return
    try {
      await apiClient.uploadPhoto(producer.id, file)
      addToast('Photo ajoutée avec succès', 'success')
      await loadProducer()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors de l\'ajout de la photo'
      addToast(errorMessage, 'error')
    }
  }

  const handleDeletePhoto = async (photoId: number) => {
    try {
      await apiClient.deletePhoto(photoId)
      addToast('Photo supprimée', 'success')
      await loadProducer()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la suppression'
      addToast(errorMessage, 'error')
    }
  }

  const handleCreateProduct = async (data: {
    name: string
    description: string
    category_id?: number
    availability_type?: 'all_year' | 'custom'
    availability_start_month?: number | null
    availability_end_month?: number | null
  }) => {
    if (!producer) return
    try {
      await apiClient.createProduct(producer.id, data)
      addToast('Produit ajouté avec succès', 'success')
      await loadProducer()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la création du produit'
      addToast(errorMessage, 'error')
      console.error('Error creating product:', err)
    }
  }

  const handleUpdateProduct = async (updatedProduct: Product) => {
    try {
      addToast('Produit modifié avec succès', 'success')
      await loadProducer()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la modification'
      addToast(errorMessage, 'error')
    }
  }

  const handleDeleteProduct = async (productId: number) => {
    try {
      await apiClient.deleteProduct(productId)
      addToast('Produit supprimé', 'success')
      await loadProducer()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la suppression'
      addToast(errorMessage, 'error')
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-lg text-gray-600">Chargement...</p>
        </div>
      </div>
    )
  }

  if (error && !producer) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <ErrorMessage message={error} onRetry={() => setError(null)} />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Barre de sauvegarde en haut */}
      <div className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b-4 border-nature-200 rounded-b-3xl shadow-nature mb-6 -mx-4 px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold text-nature-800">
              {producer ? 'Modifier mon exploitation' : 'Créer mon exploitation'}
            </h1>
            {saveStatus === 'saving' && (
              <div className="flex items-center gap-2 text-nature-600 text-sm">
                <LoadingSpinner size="sm" />
                <span>Sauvegarde...</span>
              </div>
            )}
            {saveStatus === 'saved' && (
              <div className="flex items-center gap-2 text-nature-600 text-sm font-medium">
                <span className="text-nature-500">✓</span>
                <span>Sauvegardé</span>
              </div>
            )}
            {saveStatus === 'error' && (
              <div className="flex items-center gap-2 text-red-600 text-sm font-medium">
                <span>✕</span>
                <span>Erreur</span>
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={handleManualSave}
            disabled={saveStatus === 'saving'}
            className="px-6 py-2.5 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-bold shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105 disabled:transform-none"
          >
            {saveStatus === 'saving' ? (
              <>
                <LoadingSpinner size="sm" />
                <span>Enregistrement...</span>
              </>
            ) : (
              <>
                <span>💾</span>
                <span>Enregistrer</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && <ErrorMessage message={error} className="mb-6" />}

      <form className="space-y-8" onSubmit={(e) => { e.preventDefault(); handleManualSave(); }}>
        <ProducerForm
          formData={formData}
          onFormDataChange={(data) => {
            setFormData({ ...formData, ...data })
            setSaveStatus('idle') // Réinitialiser le statut pour indiquer qu'il y a des changements
          }}
          mapCenter={mapCenter}
          mapZoom={mapZoom}
          onMapClick={handleMapClick}
          onUseMyLocation={handleUseMyLocation}
        />

        {producer && (
          <>
            <PhotoManager
              photos={producer.photos || []}
              onUpload={handlePhotoUpload}
              onDelete={handleDeletePhoto}
            />
          </>
        )}
      </form>

      {producer && (
        <>
          <div className="mt-6">
            <ProductManager
              products={products}
              onCreate={handleCreateProduct}
              onUpdate={handleUpdateProduct}
              onDelete={handleDeleteProduct}
              onRefresh={loadProducer}
            />
          </div>
          <div className="mt-6">
            <SaleModeManager
              producer={producer}
              onRefresh={async () => {
                await loadProducer()
                // Les toasts sont gérés dans SaleModeManager si nécessaire
              }}
            />
          </div>
        </>
      )}

      {/* Container pour les toasts */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  )
}
