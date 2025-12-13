'use client'

import { useState, useEffect, useRef } from 'react'
import { apiClient } from '@/lib/api'
import { CategoryIcon } from '@/components/CategoryIcon'
import { getImageUrl } from '@/lib/imageUrl'
import type { Product, ProductCategory } from '@/types'

interface ProductItemProps {
  product: Product
  onEdit: (product: Product) => void
  onDelete: () => void
  onRefresh: () => Promise<void>
}

const MONTHS = [
  { value: 1, label: 'Janvier' },
  { value: 2, label: 'Février' },
  { value: 3, label: 'Mars' },
  { value: 4, label: 'Avril' },
  { value: 5, label: 'Mai' },
  { value: 6, label: 'Juin' },
  { value: 7, label: 'Juillet' },
  { value: 8, label: 'Août' },
  { value: 9, label: 'Septembre' },
  { value: 10, label: 'Octobre' },
  { value: 11, label: 'Novembre' },
  { value: 12, label: 'Décembre' },
]

export function ProductItem({ product, onEdit, onDelete, onRefresh }: ProductItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({
    name: product.name,
    description: product.description || '',
    category_id: product.category?.id,
    availability_type: product.availability_type || 'all_year',
    availability_start_month: product.availability_start_month ?? null,
    availability_end_month: product.availability_end_month ?? null,
  })
  
  // Mettre à jour editData quand product change
  useEffect(() => {
    setEditData({
      name: product.name,
      description: product.description || '',
      category_id: product.category?.id,
      availability_type: product.availability_type || 'all_year',
      availability_start_month: product.availability_start_month ?? null,
      availability_end_month: product.availability_end_month ?? null,
    })
  }, [product])
  const [categories, setCategories] = useState<ProductCategory[]>([])
  const [saving, setSaving] = useState(false)
  const [uploadingPhoto, setUploadingPhoto] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const cats = await apiClient.getProductCategories()
        setCategories(cats)
      } catch (error) {
        console.error('Error loading categories:', error)
      }
    }
    loadCategories()
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      // Validation: si période personnalisée, les mois doivent être définis
      if (editData.availability_type === 'custom') {
        if (!editData.availability_start_month || !editData.availability_end_month) {
          alert('Les mois de début et de fin sont requis pour une période personnalisée.')
          setSaving(false)
          return
        }
        if (editData.availability_start_month > editData.availability_end_month) {
          alert('Le mois de début doit être antérieur ou égal au mois de fin.')
          setSaving(false)
          return
        }
      }
      
      // Préparer les données à envoyer
      const updateData: any = {
        name: editData.name,
        description: editData.description,
        availability_type: editData.availability_type,
      }
      
      // Envoyer category_id (peut être null pour supprimer la catégorie)
      // Si undefined, on envoie null pour supprimer la catégorie
      updateData.category_id = editData.category_id !== undefined ? editData.category_id : null
      
      // Si période personnalisée, inclure les mois
      if (editData.availability_type === 'custom') {
        updateData.availability_start_month = editData.availability_start_month
        updateData.availability_end_month = editData.availability_end_month
      } else {
        // Si "tout l'année", mettre les mois à null
        updateData.availability_start_month = null
        updateData.availability_end_month = null
      }
      
      const updated = await apiClient.updateProduct(product.id, updateData)
      // Recharger les données depuis le serveur pour avoir les dernières valeurs
      await onRefresh()
      onEdit(updated)
      setIsEditing(false)
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur lors de la modification'
      alert(errorMessage)
    } finally {
      setSaving(false)
    }
  }

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Vérifier la limite de 5 photos
    if (product.photos && product.photos.length >= 5) {
      alert('Le nombre maximum de photos (5) a été atteint pour ce produit.')
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      return
    }

    setUploadingPhoto(true)
    try {
      await apiClient.uploadProductPhoto(product.id, file)
      await onRefresh()
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur lors de l\'upload'
      alert(errorMessage)
    } finally {
      setUploadingPhoto(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDeletePhoto = async (photoId: number) => {
    if (!confirm('Supprimer cette photo ?')) return
    try {
      await apiClient.deleteProductPhoto(photoId)
      await onRefresh()
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur lors de la suppression'
      alert(errorMessage)
    }
  }

  if (isEditing) {
    return (
      <div className="bg-gradient-to-br from-nature-50 to-nature-100 p-6 rounded-3xl space-y-4 border-4 border-nature-300">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nom *</label>
          <input
            type="text"
            value={editData.name}
            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
          <select
            value={editData.category_id ?? ''}
            onChange={(e) => setEditData({ ...editData, category_id: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
          >
            <option value="">Aucune catégorie</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.display_name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            value={editData.description}
            onChange={(e) => setEditData({ ...editData, description: e.target.value })}
            rows={2}
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Période de disponibilité</label>
          <select
            value={editData.availability_type}
            onChange={(e) => setEditData({
              ...editData,
              availability_type: e.target.value as 'all_year' | 'custom',
              availability_start_month: null,
              availability_end_month: null,
            })}
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
          >
            <option value="all_year">Tout l'année</option>
            <option value="custom">Période personnalisée</option>
          </select>
        </div>
        {editData.availability_type === 'custom' && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mois de début *</label>
              <select
                value={editData.availability_start_month || ''}
                onChange={(e) => setEditData({
                  ...editData,
                  availability_start_month: e.target.value ? parseInt(e.target.value) : null,
                })}
                required
                className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
              >
                <option value="">Sélectionner</option>
                {MONTHS.map((month) => (
                  <option key={month.value} value={month.value}>
                    {month.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mois de fin *</label>
              <select
                value={editData.availability_end_month || ''}
                onChange={(e) => setEditData({
                  ...editData,
                  availability_end_month: e.target.value ? parseInt(e.target.value) : null,
                })}
                required
                className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
              >
                <option value="">Sélectionner</option>
                {MONTHS.map((month) => (
                  <option key={month.value} value={month.value}>
                    {month.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
        <div className="flex gap-2">
          <button
            onClick={handleSave}
            disabled={saving || !editData.name.trim()}
                   className="px-5 py-2 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl text-sm font-semibold disabled:opacity-50 shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105 disabled:transform-none"
          >
            {saving ? 'Enregistrement...' : 'Enregistrer'}
          </button>
          <button
            onClick={() => {
              setIsEditing(false)
              setEditData({
                name: product.name,
                description: product.description || '',
                category_id: product.category?.id,
                availability_type: product.availability_type || 'all_year',
                availability_start_month: product.availability_start_month ?? null,
                availability_end_month: product.availability_end_month ?? null,
              })
            }}
                   className="px-5 py-2 bg-earth-100 hover:bg-earth-200 text-earth-800 rounded-2xl text-sm font-medium border-2 border-earth-300 transition-all"
          >
            Annuler
          </button>
        </div>
      </div>
    )
  }

        return (
          <div className="bg-gradient-to-br from-nature-50 to-white p-6 rounded-3xl space-y-4 border-4 border-nature-200 shadow-nature">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            {product.category && <CategoryIcon category={product.category} size="sm" />}
            <h3 className="font-semibold text-lg">{product.name}</h3>
            {product.category && (
              <span className="text-sm text-gray-500">({product.category.display_name})</span>
            )}
          </div>
          {product.description && (
            <p className="text-gray-600 mt-1">{product.description}</p>
          )}
          <div className="mt-2">
            <span className="text-sm text-gray-600">
              📅 Disponibilité: {
                product.availability_type === 'all_year'
                  ? 'Tout l\'année'
                  : product.availability_start_month && product.availability_end_month
                    ? `${MONTHS.find(m => m.value === product.availability_start_month)?.label} - ${MONTHS.find(m => m.value === product.availability_end_month)?.label}`
                    : 'Non définie'
              }
            </span>
          </div>
        </div>
        <div className="flex gap-2 ml-4">
          <button
            type="button"
            onClick={() => setIsEditing(true)}
                   className="px-5 py-2 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl text-sm font-semibold shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105"
          >
            Modifier
          </button>
          <button
            type="button"
            onClick={onDelete}
                   className="px-5 py-2 bg-red-500 hover:bg-red-600 text-white rounded-2xl text-sm font-semibold shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
          >
            Supprimer
          </button>
        </div>
      </div>

      {/* Photos */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">Photos</label>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handlePhotoUpload}
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadingPhoto || (product.photos && product.photos.length >= 5)}
                   className="px-5 py-2 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl text-sm font-semibold disabled:opacity-50 shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105 disabled:transform-none"
          >
            {uploadingPhoto ? 'Upload...' : product.photos && product.photos.length >= 5 ? 'Maximum atteint (5)' : `+ Ajouter photo (${product.photos?.length || 0}/5)`}
          </button>
        </div>
        {product.photos && product.photos.length > 0 ? (
          <div className="grid grid-cols-3 gap-2">
            {product.photos.map((photo) => (
              <div key={photo.id} className="relative group">
                <img
                  src={getImageUrl(photo.image_file)}
                  alt={`${product.name} - Photo ${photo.id}`}
                  className="w-full h-24 object-cover rounded"
                  onError={(e) => {
                    // Masquer l'image en cas d'erreur
                    e.currentTarget.style.display = 'none'
                  }}
                />
                <button
                  type="button"
                  onClick={() => handleDeletePhoto(photo.id)}
                  className="absolute top-1 right-1 bg-red-600 hover:bg-red-700 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">Aucune photo</p>
        )}
      </div>
    </div>
  )
}

