'use client'

import { useState } from 'react'
import { getImageUrl } from '@/lib/imageUrl'
import { LoadingSpinner } from './LoadingSpinner'
import type { ProducerPhoto } from '@/types'

interface PhotoManagerProps {
  photos: ProducerPhoto[]
  onUpload: (file: File) => Promise<void>
  onDelete: (photoId: number) => Promise<void>
}

export function PhotoManager({ photos, onUpload, onDelete }: PhotoManagerProps) {
  const [uploading, setUploading] = useState(false)

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      await onUpload(file)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleDelete = async (photoId: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette photo ?')) return
    await onDelete(photoId)
  }

  return (
    <div className="bg-white rounded-3xl shadow-nature-lg p-8 border-4 border-nature-200">
      <h2 className="text-2xl font-bold mb-6 text-nature-800 flex items-center gap-2">
        <span className="text-3xl">📸</span>
        Photos
      </h2>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Ajouter une photo
        </label>
        <input
          type="file"
          accept="image/*"
          onChange={handlePhotoUpload}
          disabled={uploading}
          className="block w-full text-sm text-earth-700 file:mr-4 file:py-3 file:px-6 file:rounded-2xl file:border-2 file:border-nature-300 file:text-sm file:font-bold file:bg-nature-100 file:text-nature-700 hover:file:bg-nature-200 transition-all"
        />
        {uploading && <p className="mt-2 text-sm text-gray-500">Upload en cours...</p>}
      </div>
      {photos.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          {photos.map((photo) => (
            <div key={photo.id} className="relative group">
              <div className="relative h-48 rounded-2xl overflow-hidden border-4 border-nature-200 shadow-nature">
                <img
                  src={getImageUrl(photo.image_file)}
                  alt="Photo producteur"
                  className="w-full h-full object-cover"
                />
              </div>
              <button
                type="button"
                onClick={() => handleDelete(photo.id)}
                className="absolute top-3 right-3 bg-red-500 text-white px-3 py-1.5 rounded-xl text-xs font-semibold opacity-0 group-hover:opacity-100 transition-all shadow-lg"
              >
                Supprimer
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}



