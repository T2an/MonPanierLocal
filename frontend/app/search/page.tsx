'use client'

import { useEffect, useState, useCallback, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { getImageUrl } from '@/lib/imageUrl'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import type { ProducerProfile } from '@/types'
import Link from 'next/link'

function SearchPageContent() {
  const searchParams = useSearchParams()
  const query = searchParams.get('q') || ''
  const [results, setResults] = useState<ProducerProfile[]>([])
  const [loading, setLoading] = useState(true)

  const searchProducers = useCallback(async () => {
    if (!query) {
      setLoading(false)
      setResults([])
      return
    }
    setLoading(true)
    try {
      // Utiliser getProducers avec le paramètre search au lieu de searchProducers
      const data = await apiClient.getProducers({ search: query })
      setResults(data.results || [])
    } catch (err: unknown) {
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [query])

  useEffect(() => {
    searchProducers()
  }, [searchProducers])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        Résultats de recherche pour "{query}"
      </h1>

      {results.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Aucun résultat trouvé.</p>
          <Link href="/" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
            Retour à la carte
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((producer) => (
            <Link
              key={producer.id}
              href={`/producers/${producer.id}`}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
            >
              {producer.photos && producer.photos.length > 0 && (
                <div className="relative h-48">
                  <img
                    src={getImageUrl(producer.photos[0].image_file)}
                    alt={producer.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <div className="p-4">
                <h2 className="text-xl font-bold mb-2">{producer.name}</h2>
                <p className="text-sm text-gray-600 mb-2">{producer.category}</p>
                <p className="text-sm text-gray-500">{producer.address}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    }>
      <SearchPageContent />
    </Suspense>
  )
}
