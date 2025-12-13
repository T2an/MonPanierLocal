'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { PRODUCER_CATEGORIES } from '@/lib/constants'

const CATEGORIES = [
  { value: '', label: 'Tous' },
  ...PRODUCER_CATEGORIES,
]

export function FilterBar() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedCategory, setSelectedCategory] = useState('')

  useEffect(() => {
    // Lire la catégorie depuis l'URL
    const category = searchParams.get('category') || ''
    setSelectedCategory(category)
  }, [searchParams])

  const handleFilterChange = (category: string) => {
    setSelectedCategory(category)
    const currentSearch = searchParams.get('q')
    const params = new URLSearchParams()
    if (category) {
      params.set('category', category)
    }
    if (currentSearch) {
      params.set('q', currentSearch)
    }
    const queryString = params.toString()
    router.push(queryString ? `/?${queryString}` : '/')
  }

  return (
    <div className="flex gap-2 overflow-x-auto">
      {CATEGORIES.map((category) => (
        <button
          key={category.value}
          onClick={() => handleFilterChange(category.value)}
          className={`px-5 py-2.5 rounded-2xl text-sm font-semibold whitespace-nowrap transition-all ${
            selectedCategory === category.value
              ? 'bg-nature-500 text-white shadow-nature border-2 border-nature-600 transform scale-105'
              : 'bg-white text-earth-700 hover:bg-nature-50 border-2 border-nature-200 hover:border-nature-300'
          }`}
        >
          {category.label}
        </button>
      ))}
    </div>
  )
}

