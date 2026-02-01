'use client'

import { useState, useEffect, type ReactNode } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { PRODUCER_CATEGORIES } from '@/lib/constants'

// Export des couleurs pour les réutiliser dans la carte
// Palette unique avec des couleurs bien distinctes, sans doublons ni similitudes
// Chaque activité a une couleur vraiment différente pour faciliter l'identification visuelle
export const CATEGORY_COLORS: Record<string, { bg: string; border: string; hex: string }> = {
  'maraîchage': { bg: 'bg-emerald-500', border: 'border-emerald-600', hex: '#10b981' },      // Vert émeraude (légumes frais)
  'élevage': { bg: 'bg-stone-700', border: 'border-stone-800', hex: '#44403c' },             // Marron/gris foncé (bétail)
  'apiculture': { bg: 'bg-yellow-400', border: 'border-yellow-500', hex: '#facc15' },          // Jaune vif (miel)
  'arboriculture': { bg: 'bg-green-600', border: 'border-green-700', hex: '#16a34a' },       // Vert forêt (arbres fruitiers)
  'céréaliculture': { bg: 'bg-amber-500', border: 'border-amber-600', hex: '#f59e0b' },      // Ambre doré (blé, céréales)
  'pêche': { bg: 'bg-cyan-500', border: 'border-cyan-600', hex: '#06b6d4' },                  // Cyan (eau, poissons)
  'brasserie': { bg: 'bg-indigo-500', border: 'border-indigo-600', hex: '#6366f1' },          // Indigo (bière)
  'distillerie': { bg: 'bg-purple-600', border: 'border-purple-700', hex: '#9333ea' },        // Violet (alcools forts)
  'fromagerie': { bg: 'bg-teal-500', border: 'border-teal-600', hex: '#14b8a6' },             // Teal (fromage)
  'boulangerie': { bg: 'bg-orange-500', border: 'border-orange-600', hex: '#f97316' },        // Orange (pain)
  'viticulture': { bg: 'bg-rose-600', border: 'border-rose-700', hex: '#e11d48' },           // Rose foncé (vin)
  'charcuterie': { bg: 'bg-red-600', border: 'border-red-700', hex: '#dc2626' },             // Rouge (viande)
  'autre': { bg: 'bg-slate-500', border: 'border-slate-600', hex: '#64748b' },               // Gris ardoise (neutre)
}

const CATEGORIES = [
  ...PRODUCER_CATEGORIES.map(cat => ({
    ...cat,
    icon: getCategoryIcon(cat.value),
    color: CATEGORY_COLORS[cat.value] || CATEGORY_COLORS['autre']
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

interface FilterSidebarProps {
  children?: ReactNode
  isCollapsed?: boolean
  onToggleCollapse?: () => void
}

export function FilterSidebar({ children, isCollapsed = false, onToggleCollapse }: FilterSidebarProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])

  useEffect(() => {
    const categories = searchParams.get('categories')
    if (categories) {
      setSelectedCategories(categories.split(',').filter(Boolean))
    } else {
      setSelectedCategories([])
    }
  }, [searchParams])

  const handleCategoryToggle = (category: string) => {
    let newCategories: string[]
    
    if (selectedCategories.includes(category)) {
      // Retirer la catégorie
      newCategories = selectedCategories.filter(c => c !== category)
    } else {
      // Ajouter la catégorie
      newCategories = [...selectedCategories, category]
    }
    
    setSelectedCategories(newCategories)
    
    const currentSearch = searchParams.get('q')
    const params = new URLSearchParams()
    if (newCategories.length > 0) {
      params.set('categories', newCategories.join(','))
    }
    if (currentSearch) {
      params.set('q', currentSearch)
    }
    const queryString = params.toString()
    router.push(queryString ? `/?${queryString}` : '/')
  }
  
  const clearAllCategories = () => {
    setSelectedCategories([])
    const currentSearch = searchParams.get('q')
    const params = new URLSearchParams()
    if (currentSearch) {
      params.set('q', currentSearch)
    }
    const queryString = params.toString()
    router.push(queryString ? `/?${queryString}` : '/')
  }
  
  const selectAllCategories = () => {
    const allCats = CATEGORIES.map(c => c.value)
    setSelectedCategories(allCats)
    const currentSearch = searchParams.get('q')
    const params = new URLSearchParams()
    params.set('categories', allCats.join(','))
    if (currentSearch) {
      params.set('q', currentSearch)
    }
    const queryString = params.toString()
    router.push(queryString ? `/?${queryString}` : '/')
  }

  return (
    <>
      {/* Sidebar */}
      <div 
        className={`fixed left-0 top-0 h-full bg-gradient-to-b from-white to-nature-50/30 border-r-4 border-nature-400 shadow-nature-lg z-40 overflow-y-auto transition-all duration-300 ease-in-out ${
          isCollapsed ? 'w-0 -translate-x-full' : 'w-96'
        }`}
      >
        <div className="w-96">
          {/* Header avec bouton de fermeture */}
          <div className="sticky top-0 bg-gradient-to-b from-white to-nature-50 border-b-4 border-nature-300 z-10 p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-nature-800 flex items-center gap-2">
                <span className="text-2xl">🔍</span>
                <span>Recherche</span>
              </h2>
              {onToggleCollapse && (
                <button
                  onClick={onToggleCollapse}
                  className="p-2.5 bg-nature-100 hover:bg-nature-200 rounded-xl transition-colors text-nature-700 hover:text-nature-800 flex items-center gap-1.5"
                  title="Masquer le panneau"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                  </svg>
                  <span className="text-xs font-medium">Masquer</span>
                </button>
              )}
            </div>
          </div>

          <div className="p-5 space-y-5">
            {/* Zone de recherche */}
            {children && (
              <div className="bg-white/90 backdrop-blur rounded-2xl border-2 border-nature-200 shadow-nature p-5">
                {children}
              </div>
            )}

            {/* Catégories */}
            <div>
              <div className="flex items-center justify-between mb-3 px-1">
                <h3 className="text-sm font-bold text-nature-700 flex items-center gap-2">
                  <span>🏷️</span>
                  <span>Filtrer par activité</span>
                </h3>
                <div className="flex gap-1">
                  <button
                    onClick={selectAllCategories}
                    className="text-xs px-2 py-1 bg-nature-100 hover:bg-nature-200 text-nature-700 rounded-lg transition-colors"
                    title="Tout sélectionner"
                  >
                    Tout
                  </button>
                  <button
                    onClick={clearAllCategories}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors"
                    title="Tout désélectionner"
                  >
                    Aucun
                  </button>
                </div>
              </div>
              
              {/* Indication du nombre sélectionné */}
              {selectedCategories.length > 0 && (
                <p className="text-xs text-nature-600 mb-2 px-1">
                  {selectedCategories.length} activité{selectedCategories.length > 1 ? 's' : ''} sélectionnée{selectedCategories.length > 1 ? 's' : ''}
                </p>
              )}
              
              <div className="space-y-1.5">
                {CATEGORIES.map((category) => {
                  const isSelected = selectedCategories.includes(category.value)
                  return (
                    <button
                      key={category.value}
                      onClick={() => handleCategoryToggle(category.value)}
                      className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-3 group ${
                        isSelected
                          ? `${category.color.bg} text-white shadow-md ${category.color.border} border-2`
                          : 'bg-white text-earth-700 hover:bg-gray-50 border-2 border-gray-100 hover:border-gray-200'
                      }`}
                    >
                      {/* Pastille de couleur */}
                      <span 
                        className={`w-4 h-4 rounded-full flex-shrink-0 border-2 ${
                          isSelected 
                            ? 'bg-white/30 border-white/50' 
                            : `${category.color.bg} ${category.color.border}`
                        }`}
                      />
                      <span className={`text-lg flex-shrink-0 transition-transform group-hover:scale-110 ${
                        isSelected ? 'filter drop-shadow-md' : ''
                      }`}>
                        {category.icon}
                      </span>
                      <span className="flex-1 truncate">{category.label}</span>
                      {/* Checkbox visuelle */}
                      <span className={`w-5 h-5 rounded-md flex items-center justify-center text-xs border-2 transition-all ${
                        isSelected 
                          ? 'bg-white/20 border-white/40 text-white' 
                          : 'bg-white border-gray-300'
                      }`}>
                        {isSelected && '✓'}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bouton pour réouvrir la sidebar quand elle est fermée */}
      {isCollapsed && onToggleCollapse && (
        <button
          onClick={onToggleCollapse}
          className="fixed left-4 top-24 z-50 bg-nature-500 hover:bg-nature-600 text-white px-4 py-3 rounded-2xl shadow-nature-lg transition-all hover:scale-105 flex items-center gap-2"
          title="Afficher les filtres"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
          </svg>
          <span className="text-sm font-semibold">Filtres</span>
        </button>
      )}
    </>
  )
}
