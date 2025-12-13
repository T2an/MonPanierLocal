'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { getImageUrl } from '@/lib/imageUrl'
import type { ProducerProfile } from '@/types'

interface ProducerListProps {
  producers: ProducerProfile[]
  onProducerClick?: (producer: ProducerProfile) => void
  distances?: number[]
}

export function ProducerList({ producers, onProducerClick, distances }: ProducerListProps) {
  const [selectedProducer, setSelectedProducer] = useState<number | null>(null)

  if (producers.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Aucun producteur trouvé.</p>
      </div>
    )
  }

  const handleClick = (producer: ProducerProfile) => {
    setSelectedProducer(producer.id)
    if (onProducerClick) {
      onProducerClick(producer)
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 p-6">
      {producers.map((producer, index) => (
        <Link
          key={producer.id}
          href={`/producers/${producer.id}`}
          onClick={() => handleClick(producer)}
          className={`bg-white rounded-3xl shadow-nature overflow-hidden hover:shadow-nature-lg transition-all duration-300 transform hover:scale-[1.02] border-4 ${
            selectedProducer === producer.id ? 'border-nature-500 ring-4 ring-nature-200' : 'border-nature-200 hover:border-nature-400'
          }`}
        >
          {producer.photos && producer.photos.length > 0 && (
            <div className="relative h-56 rounded-t-3xl overflow-hidden">
              <Image
                src={getImageUrl(producer.photos[0].image_file)}
                alt={producer.name}
                fill
                className="object-cover"
              />
            </div>
          )}
          <div className="p-6 bg-gradient-to-b from-white to-nature-50/30">
            <div className="flex items-start justify-between mb-3">
              <h2 className="text-xl font-bold text-nature-800 flex-1">{producer.name}</h2>
              <span className="inline-block bg-nature-200 text-nature-800 text-xs font-bold px-3 py-1.5 rounded-2xl whitespace-nowrap ml-3 border-2 border-nature-300">
                {producer.category}
              </span>
            </div>
            <p className="text-sm text-earth-700 mb-3 line-clamp-2 leading-relaxed">{producer.description || 'Aucune description'}</p>
            <div className="space-y-2 mb-3">
              {distances && distances[index] !== undefined && (
                <p className="text-xs text-nature-700 font-bold bg-nature-100 px-3 py-1.5 rounded-xl inline-block border-2 border-nature-300">
                  📏 {distances[index].toFixed(1)} km
                </p>
              )}
              <p className="text-xs text-nature-600 font-medium">
                📍 {producer.address}
              </p>
              {producer.phone && (
                <p className="text-xs text-nature-600 font-medium">
                  📞 {producer.phone}
                </p>
              )}
            </div>
            {producer.products && producer.products.length > 0 && (
              <div className="mt-4 pt-3 border-t-2 border-nature-200 flex flex-wrap gap-2">
                {producer.products.slice(0, 3).map((product) => (
                  <span
                    key={product.id}
                    className="inline-block bg-nature-100 text-nature-700 text-xs font-medium px-3 py-1.5 rounded-xl border border-nature-300"
                  >
                    {product.name}
                  </span>
                ))}
                {producer.products.length > 3 && (
                  <span className="inline-block bg-earth-100 text-earth-700 text-xs font-medium px-3 py-1.5 rounded-xl border border-earth-300">
                    +{producer.products.length - 3}
                  </span>
                )}
              </div>
            )}
          </div>
        </Link>
      ))}
    </div>
  )
}

