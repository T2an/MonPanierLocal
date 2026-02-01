'use client'

import { useMemo } from 'react'
import type { Product } from '@/types'

interface ProductCalendarProps {
  products: Product[]
}

const MONTHS = [
  { short: 'J', full: 'Janvier', value: 1 },
  { short: 'F', full: 'Février', value: 2 },
  { short: 'M', full: 'Mars', value: 3 },
  { short: 'A', full: 'Avril', value: 4 },
  { short: 'M', full: 'Mai', value: 5 },
  { short: 'J', full: 'Juin', value: 6 },
  { short: 'J', full: 'Juillet', value: 7 },
  { short: 'A', full: 'Août', value: 8 },
  { short: 'S', full: 'Septembre', value: 9 },
  { short: 'O', full: 'Octobre', value: 10 },
  { short: 'N', full: 'Novembre', value: 11 },
  { short: 'D', full: 'Décembre', value: 12 },
]

// Palette de couleurs harmonieuses pour les produits
const COLORS = [
  { bg: 'bg-emerald-500', light: 'bg-emerald-100', text: 'text-emerald-700', border: 'border-emerald-300' },
  { bg: 'bg-amber-500', light: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-300' },
  { bg: 'bg-rose-500', light: 'bg-rose-100', text: 'text-rose-700', border: 'border-rose-300' },
  { bg: 'bg-sky-500', light: 'bg-sky-100', text: 'text-sky-700', border: 'border-sky-300' },
  { bg: 'bg-violet-500', light: 'bg-violet-100', text: 'text-violet-700', border: 'border-violet-300' },
  { bg: 'bg-orange-500', light: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-300' },
  { bg: 'bg-teal-500', light: 'bg-teal-100', text: 'text-teal-700', border: 'border-teal-300' },
  { bg: 'bg-pink-500', light: 'bg-pink-100', text: 'text-pink-700', border: 'border-pink-300' },
  { bg: 'bg-indigo-500', light: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300' },
  { bg: 'bg-lime-500', light: 'bg-lime-100', text: 'text-lime-700', border: 'border-lime-300' },
]

// Obtenir le mois actuel (1-12)
const getCurrentMonth = () => new Date().getMonth() + 1

export function ProductCalendar({ products }: ProductCalendarProps) {
  const currentMonth = getCurrentMonth()

  // Préparer les données des produits avec leurs couleurs
  const productsWithColors = useMemo(() => {
    return products.map((product, index) => ({
      ...product,
      color: COLORS[index % COLORS.length],
    }))
  }, [products])

  // Vérifier si un mois est dans la période de disponibilité d'un produit
  const isMonthAvailable = (product: Product, month: number): boolean => {
    if (product.availability_type === 'all_year') return true
    if (!product.availability_start_month || !product.availability_end_month) return false
    
    const start = product.availability_start_month
    const end = product.availability_end_month
    
    // Gérer le cas où la période traverse la fin d'année (ex: Nov -> Fév)
    if (start <= end) {
      return month >= start && month <= end
    } else {
      return month >= start || month <= end
    }
  }

  // Compter les produits disponibles par mois
  const availabilityByMonth = useMemo(() => {
    return MONTHS.map((month) => ({
      month,
      count: products.filter((p) => isMonthAvailable(p, month.value)).length,
    }))
  }, [products])

  if (products.length === 0) {
    return (
      <div className="bg-gradient-to-br from-nature-50 to-white rounded-2xl border-2 border-nature-200 p-8 text-center">
        <div className="text-4xl mb-3">📅</div>
        <p className="text-gray-500">Ajoutez des produits pour voir le calendrier de disponibilité</p>
      </div>
    )
  }

  // Calculer les produits disponibles par mois pour l'empilement
  const productsByMonth = useMemo(() => {
    return MONTHS.map((month) => {
      const availableProducts = productsWithColors.filter((product) =>
        isMonthAvailable(product, month.value)
      )
      return {
        month,
        products: availableProducts,
      }
    })
  }, [productsWithColors])

  // Calculer la hauteur maximale nécessaire (pour le mois avec le plus de produits)
  const maxProductsPerMonth = Math.max(...productsByMonth.map((m) => m.products.length), 1)
  // Hauteur minimale de 80px, + 28px par produit supplémentaire
  const cellHeight = Math.max(80, 52 + maxProductsPerMonth * 28)

  return (
    <div className="bg-gradient-to-br from-white to-nature-50/30 rounded-2xl border-2 border-nature-200 overflow-hidden">
      {/* Header */}
      <div className="bg-nature-600 text-white px-6 py-4">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <span>📅</span>
          <span>Calendrier de disponibilité</span>
        </h3>
        <p className="text-nature-100 text-sm mt-1">
          {products.length} produit{products.length > 1 ? 's' : ''} • Mois actuel : {MONTHS[currentMonth - 1].full}
        </p>
      </div>

      {/* Calendrier avec blocs empilés */}
      <div className="p-4 overflow-x-auto">
        <div className="grid grid-cols-[200px_repeat(12,_1fr)] gap-2 min-w-[900px]">
          {/* En-tête : Légende des produits */}
          <div className="sticky left-0 z-10 bg-white border-r-2 border-nature-200 pr-3">
            <div className="text-sm font-semibold text-gray-700 mb-2">Produits</div>
            <div className="space-y-1.5">
              {productsWithColors.map((product) => (
                <div
                  key={product.id}
                  className="flex items-center gap-2 text-xs"
                  title={product.name}
                >
                  <div className={`w-3 h-3 rounded-full ${product.color.bg} flex-shrink-0 border border-white shadow-sm`} />
                  <span className="text-gray-700 truncate font-medium">{product.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Colonnes des mois avec blocs empilés */}
          {productsByMonth.map(({ month, products: monthProducts }) => {
            const isCurrentMonth = month.value === currentMonth
            
            return (
              <div
                key={month.value}
                className={`flex flex-col ${
                  isCurrentMonth ? 'bg-nature-100/50 ring-2 ring-nature-400 rounded-lg p-1' : ''
                }`}
              >
                {/* En-tête du mois */}
                <div
                  className={`text-center py-2 px-1 text-xs font-semibold mb-1 rounded-t ${
                    isCurrentMonth
                      ? 'bg-nature-500 text-white'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                  title={month.full}
                >
                  <span className="hidden sm:inline">{month.full.slice(0, 3)}</span>
                  <span className="sm:hidden">{month.short}</span>
                </div>

                {/* Zone d'empilement des produits */}
                <div
                  className="flex-1 flex flex-col gap-0.5 p-1 bg-white/50 rounded-b border border-gray-200 relative group"
                  style={{ minHeight: `${cellHeight}px` }}
                >
                  {monthProducts.length > 0 ? (
                    monthProducts.map((product, index) => {
                      // Calculer les arrondis selon la position dans la pile
                      let roundedClass = 'rounded'
                      if (monthProducts.length === 1) {
                        roundedClass = 'rounded'
                      } else if (index === 0) {
                        roundedClass = 'rounded-t'
                      } else if (index === monthProducts.length - 1) {
                        roundedClass = 'rounded-b'
                      } else {
                        roundedClass = ''
                      }

                      // Calculer la hauteur de chaque bloc (répartition équitable)
                      const blockHeight = `${100 / monthProducts.length}%`

                      return (
                        <div
                          key={product.id}
                          className={`${product.color.bg} ${roundedClass} flex items-center justify-center px-1.5 py-1 text-white text-[10px] font-medium shadow-sm hover:shadow-lg hover:scale-[1.02] transition-all cursor-pointer relative group/product-block`}
                          style={{
                            height: blockHeight,
                            minHeight: '28px',
                            flex: `0 0 ${blockHeight}`,
                          }}
                          title={`${product.name} - ${month.full}`}
                        >
                          {/* Nom du produit (visible si assez de place) */}
                          {monthProducts.length <= 4 ? (
                            <span className="truncate text-center leading-tight px-1 text-[11px] font-semibold drop-shadow-sm">
                              {product.name}
                            </span>
                          ) : (
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className={`w-4 h-4 rounded-full ${product.color.bg} border-2 border-white/90 shadow-md`} />
                            </div>
                          )}

                          {/* Tooltip au survol */}
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover/product-block:opacity-100 transition-opacity pointer-events-none z-20 delay-75">
                            <div className="bg-gray-900 text-white text-xs py-1.5 px-2.5 rounded-lg whitespace-nowrap shadow-xl">
                              <div className="font-semibold">{product.name}</div>
                              <div className="text-[10px] opacity-80 mt-0.5">{month.full}</div>
                            </div>
                            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
                          </div>
                        </div>
                      )
                    })
                  ) : (
                    <div className="flex-1 flex items-center justify-center text-gray-300 text-xs">
                      <span className="opacity-50">—</span>
                    </div>
                  )}
                  
                  {/* Compteur de produits disponibles (en bas à droite) */}
                  {monthProducts.length > 1 && (
                    <div className="absolute bottom-1 right-1 bg-black/70 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full shadow-lg">
                      {monthProducts.length}
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Résumé par mois */}
      <div className="border-t-2 border-nature-200 px-6 py-4 bg-nature-50/50">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-gray-700">Produits disponibles par mois</span>
          <span className="text-xs text-gray-500">Survolez pour plus de détails</span>
        </div>
        <div className="flex gap-1">
          {availabilityByMonth.map(({ month, count }) => {
            const percentage = products.length > 0 ? (count / products.length) * 100 : 0
            const isCurrentMonth = month.value === currentMonth
            
            return (
              <div
                key={month.value}
                className={`flex-1 group relative ${isCurrentMonth ? 'ring-2 ring-nature-500 ring-offset-1 rounded' : ''}`}
                title={`${month.full}: ${count} produit${count > 1 ? 's' : ''}`}
              >
                <div className="h-12 bg-gray-200 rounded-sm overflow-hidden flex flex-col-reverse">
                  <div
                    className={`transition-all ${
                      percentage > 75 ? 'bg-emerald-500' :
                      percentage > 50 ? 'bg-nature-500' :
                      percentage > 25 ? 'bg-amber-500' :
                      percentage > 0 ? 'bg-orange-500' : 'bg-gray-300'
                    }`}
                    style={{ height: `${percentage}%` }}
                  />
                </div>
                <div className={`text-center text-xs mt-1 ${isCurrentMonth ? 'font-bold text-nature-700' : 'text-gray-500'}`}>
                  {month.short}
                </div>
                
                {/* Tooltip au survol */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                  <div className="bg-gray-900 text-white text-xs py-1 px-2 rounded whitespace-nowrap">
                    {month.full}: {count}/{products.length}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Légende */}
      <div className="border-t-2 border-nature-200 px-6 py-4">
        <div className="text-sm font-semibold text-gray-700 mb-3">Légende</div>
        <div className="flex flex-wrap gap-3">
          {productsWithColors.map((product) => (
            <div
              key={product.id}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${product.color.light} ${product.color.border} border`}
            >
              <div className={`w-2.5 h-2.5 rounded-full ${product.color.bg}`} />
              <span className={`text-sm font-medium ${product.color.text}`}>{product.name}</span>
              {product.availability_type === 'all_year' && (
                <span className="text-xs opacity-60">Toute l'année</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
