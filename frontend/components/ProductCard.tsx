'use client'

import { useState, useEffect } from 'react'
import { CategoryIcon } from '@/components/CategoryIcon'
import { getImageUrl } from '@/lib/imageUrl'
import type { Product } from '@/types'

interface ProductCardProps {
  product: Product
}

const MONTHS = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
]

export function ProductCard({ product }: ProductCardProps) {
  const [carouselOpen, setCarouselOpen] = useState(false)
  const [carouselIndex, setCarouselIndex] = useState(0)

  const getAvailabilityText = () => {
    if (product.availability_type === 'all_year') {
      return 'Tout l\'année'
    }
    if (product.availability_type === 'custom' && product.availability_start_month && product.availability_end_month) {
      const start = MONTHS[product.availability_start_month - 1]
      const end = MONTHS[product.availability_end_month - 1]
      return `${start} à ${end}`
    }
    return 'Non définie'
  }

  // Récupérer les photos valides
  const validPhotos = product.photos?.filter(p => p.image_file) || []
  const photoCount = validPhotos.length

  // Ouvrir le carrousel à partir d'une photo spécifique
  const openCarousel = (index: number) => {
    setCarouselIndex(index)
    setCarouselOpen(true)
  }

  // Navigation dans le carrousel
  const nextPhoto = () => {
    setCarouselIndex((prev) => (prev + 1) % photoCount)
  }

  const prevPhoto = () => {
    setCarouselIndex((prev) => (prev - 1 + photoCount) % photoCount)
  }

  // Navigation au clavier
  useEffect(() => {
    if (!carouselOpen || photoCount === 0) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        e.preventDefault()
        setCarouselIndex((prev) => (prev + 1) % photoCount)
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        setCarouselIndex((prev) => (prev - 1 + photoCount) % photoCount)
      } else if (e.key === 'Escape') {
        e.preventDefault()
        setCarouselOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [carouselOpen, photoCount])

  // Fonction pour déterminer le layout de la grille selon le nombre de photos
  const getGridLayout = () => {
    if (photoCount === 0) return null
    if (photoCount === 1) {
      // 1 photo : prend toute la zone
      return (
        <div className="w-full h-full cursor-pointer" onClick={() => openCarousel(0)}>
          <img
            src={getImageUrl(validPhotos[0].image_file)}
            alt={`${product.name} - Photo 1`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        </div>
      )
    }
    if (photoCount === 2) {
      // 2 photos : côte à côte
      return (
        <div className="grid grid-cols-2 gap-1 h-full">
          {validPhotos.map((photo, index) => (
            <div
              key={photo.id}
              className="cursor-pointer overflow-hidden"
              onClick={() => openCarousel(index)}
            >
              <img
                src={getImageUrl(photo.image_file)}
                alt={`${product.name} - Photo ${index + 1}`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.style.display = 'none'
                }}
              />
            </div>
          ))}
        </div>
      )
    }
    if (photoCount === 3) {
      // 3 photos : 2 en haut, 1 en bas
      return (
        <div className="grid grid-cols-2 gap-1 h-full">
          <div
            className="row-span-1 cursor-pointer overflow-hidden"
            onClick={() => openCarousel(0)}
          >
            <img
              src={getImageUrl(validPhotos[0].image_file)}
              alt={`${product.name} - Photo 1`}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
          <div
            className="row-span-1 cursor-pointer overflow-hidden"
            onClick={() => openCarousel(1)}
          >
            <img
              src={getImageUrl(validPhotos[1].image_file)}
              alt={`${product.name} - Photo 2`}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
          <div
            className="col-span-2 cursor-pointer overflow-hidden"
            onClick={() => openCarousel(2)}
          >
            <img
              src={getImageUrl(validPhotos[2].image_file)}
              alt={`${product.name} - Photo 3`}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        </div>
      )
    }
    if (photoCount === 4) {
      // 4 photos : grille 2x2
      return (
        <div className="grid grid-cols-2 gap-1 h-full">
          {validPhotos.map((photo, index) => (
            <div
              key={photo.id}
              className="cursor-pointer overflow-hidden"
              onClick={() => openCarousel(index)}
            >
              <img
                src={getImageUrl(photo.image_file)}
                alt={`${product.name} - Photo ${index + 1}`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.style.display = 'none'
                }}
              />
            </div>
          ))}
        </div>
      )
    }
    // 5 photos : 2 en haut, 3 en bas
    return (
      <div className="grid grid-cols-3 gap-1 h-full">
        <div
          className="row-span-1 col-span-2 cursor-pointer overflow-hidden"
          onClick={() => openCarousel(0)}
        >
          <img
            src={getImageUrl(validPhotos[0].image_file)}
            alt={`${product.name} - Photo 1`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        </div>
        <div
          className="row-span-1 cursor-pointer overflow-hidden"
          onClick={() => openCarousel(1)}
        >
          <img
            src={getImageUrl(validPhotos[1].image_file)}
            alt={`${product.name} - Photo 2`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        </div>
        {validPhotos.slice(2, 5).map((photo, index) => (
          <div
            key={photo.id}
            className="cursor-pointer overflow-hidden"
            onClick={() => openCarousel(index + 2)}
          >
            <img
              src={getImageUrl(photo.image_file)}
              alt={`${product.name} - Photo ${index + 3}`}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        ))}
      </div>
    )
  }

  return (
    <>
      <div className="bg-white rounded-3xl shadow-nature-lg overflow-hidden h-full flex flex-col border-4 border-nature-200 hover:border-nature-400 transition-all duration-300 hover:shadow-nature-lg transform hover:scale-[1.02]" style={{ minHeight: '400px' }}>
        {/* Section images - Taille fixe avec grille organisée */}
        <div className="relative h-48 bg-gradient-to-br from-nature-100 to-nature-50">
          {photoCount > 0 ? (
            <>
              {getGridLayout()}
              {/* Badge nombre de photos si plus d'une */}
              {photoCount > 1 && (
                <div className="absolute bottom-3 right-3 bg-black/60 backdrop-blur-sm text-white text-xs font-bold px-3 py-1.5 rounded-xl z-10">
                  {photoCount} photos
                </div>
              )}
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-nature-100 to-nature-50">
              <span className="text-nature-500 text-sm font-medium">🌱 Aucune photo</span>
            </div>
          )}
          
          {/* Étiquette catégorie en haut à gauche */}
          {product.category && (
            <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-sm rounded-2xl px-4 py-2 flex items-center gap-2 shadow-nature z-10 border-2 border-nature-200">
              <CategoryIcon category={product.category} size="sm" />
              <span className="text-xs font-semibold text-nature-700">{product.category.display_name}</span>
            </div>
          )}
        </div>

        {/* Section contenu - 50% de la hauteur */}
        <div className="p-6 flex-1 flex flex-col bg-gradient-to-b from-white to-nature-50/30">
          <h3 className="font-bold text-xl mb-3 text-nature-800">{product.name}</h3>
          
          <div className="mb-3">
            <span className="text-sm text-nature-600 font-medium bg-nature-100 px-3 py-1.5 rounded-xl inline-block">
              📅 {getAvailabilityText()}
            </span>
          </div>
          
          {product.description && (
            <p className="text-earth-700 text-sm flex-1 line-clamp-3 leading-relaxed">{product.description}</p>
          )}
        </div>
      </div>

      {/* Carrousel modal */}
      {carouselOpen && photoCount > 0 && (
        <div
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
          onClick={() => setCarouselOpen(false)}
        >
          <div className="relative max-w-5xl max-h-full w-full">
            {/* Image principale */}
            <div className="relative">
              <img
                src={getImageUrl(validPhotos[carouselIndex].image_file)}
                alt={`${product.name} - Photo ${carouselIndex + 1}`}
                className="max-w-full max-h-[85vh] object-contain rounded-2xl mx-auto"
                onClick={(e) => e.stopPropagation()}
              />
              
              {/* Bouton fermer */}
              <button
                onClick={() => setCarouselOpen(false)}
                className="absolute top-4 right-4 bg-white/90 hover:bg-white rounded-full w-12 h-12 flex items-center justify-center text-3xl font-bold shadow-lg transition-all hover:scale-110 z-20"
              >
                ×
              </button>

              {/* Bouton précédent */}
              {photoCount > 1 && (
                <>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      prevPhoto()
                    }}
                    className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full w-12 h-12 flex items-center justify-center text-2xl font-bold shadow-lg transition-all hover:scale-110 z-20"
                  >
                    ‹
                  </button>
                  
                  {/* Bouton suivant */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      nextPhoto()
                    }}
                    className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full w-12 h-12 flex items-center justify-center text-2xl font-bold shadow-lg transition-all hover:scale-110 z-20"
                  >
                    ›
                  </button>
                </>
              )}

              {/* Indicateurs de position */}
              {photoCount > 1 && (
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-20">
                  {validPhotos.map((_, index) => (
                    <button
                      key={index}
                      onClick={(e) => {
                        e.stopPropagation()
                        setCarouselIndex(index)
                      }}
                      className={`w-3 h-3 rounded-full transition-all ${
                        index === carouselIndex
                          ? 'bg-white scale-125'
                          : 'bg-white/50 hover:bg-white/75'
                      }`}
                    />
                  ))}
                </div>
              )}

              {/* Compteur de photos */}
              <div className="absolute bottom-4 right-4 bg-black/60 backdrop-blur-sm text-white text-sm font-semibold px-3 py-1.5 rounded-xl z-20">
                {carouselIndex + 1} / {photoCount}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

