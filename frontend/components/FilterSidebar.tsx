'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { PRODUCER_CATEGORIES } from '@/lib/constants'

const CATEGORIES = [
  { value: '', label: 'Tous', icon: '🌾' },
  ...PRODUCER_CATEGORIES.map(cat => ({
    ...cat,
    icon: getCategoryIcon(cat.value)
  }))
]

function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    'maraîchage': '🥬',
    'élevage': '🐄',
    'apiculture': '🐝',
    'arboriculture': '🌳',
    'céréaliculture': '🌾',
    'pêche': '🐟',
    'brasserie': '🍺',
    'distillerie': '🥃',
    'fromagerie': '🧀',
    'boulangerie': '🥖',
    'viticulture': '🍷',
    'charcuterie': '🥓',
    'autre': '📦',
  }
  return icons[category] || '📦'
}

export function FilterSidebar() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedCategory, setSelectedCategory] = useState('')

  useEffect(() => {
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
    <div className="fixed left-0 top-0 h-full w-72 bg-gradient-to-b from-white to-nature-50/30 border-r-4 border-nature-400 shadow-nature-lg z-40 overflow-y-auto">
      <div className="sticky top-0 bg-gradient-to-b from-white to-nature-50 border-b-4 border-nature-300 z-10 p-5 backdrop-blur-sm">
        <h2 className="text-xl font-bold text-nature-800 mb-1 flex items-center gap-2">
          <span className="text-3xl">🔍</span>
          <span>Activités</span>
        </h2>
        <p className="text-xs text-nature-600 mt-1">Filtrer les producteurs</p>
      </div>
      <div className="p-4 space-y-2.5">
        {CATEGORIES.map((category) => (
          <button
            key={category.value}
            onClick={() => handleFilterChange(category.value)}
            className={`w-full text-left px-5 py-4 rounded-2xl text-sm font-bold transition-all duration-200 flex items-center gap-3 group ${
              selectedCategory === category.value
                ? 'bg-nature-500 text-white shadow-nature-lg border-4 border-nature-600 transform scale-[1.03]'
                : 'bg-white text-earth-700 hover:bg-nature-100 border-2 border-nature-200 hover:border-nature-400 hover:shadow-nature'
            }`}
          >
            <span className={`text-2xl flex-shrink-0 transition-transform group-hover:scale-110 ${
              selectedCategory === category.value ? 'filter drop-shadow-lg' : ''
            }`}>
              {category.icon}
            </span>
            <span className="flex-1 font-semibold">{category.label}</span>
            {selectedCategory === category.value && (
              <span className="text-white text-xl font-bold animate-pulse">✓</span>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

