'use client'

import { useState, useEffect } from 'react'
import { ProductItem } from '@/app/producer/edit/ProductItem'
import { apiClient } from '@/lib/api'
import type { Product, ProductCategory } from '@/types'

interface ProductManagerProps {
  products: Product[]
  onCreate: (data: {
    name: string
    description: string
    category_id?: number
    availability_type?: 'all_year' | 'custom'
    availability_start_month?: number | null
    availability_end_month?: number | null
  }) => Promise<void>
  onUpdate: (product: Product) => void
  onDelete: (id: number) => Promise<void>
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

export function ProductManager({ products, onCreate, onUpdate, onDelete, onRefresh }: ProductManagerProps) {
  const [newProduct, setNewProduct] = useState({
    name: '',
    description: '',
    category_id: undefined as number | undefined,
    availability_type: 'all_year' as 'all_year' | 'custom',
    availability_start_month: null as number | null,
    availability_end_month: null as number | null,
  })
  const [categories, setCategories] = useState<ProductCategory[]>([])
  const [loadingCategories, setLoadingCategories] = useState(true)

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const cats = await apiClient.getProductCategories()
        setCategories(cats)
      } catch (error) {
        console.error('Error loading categories:', error)
      } finally {
        setLoadingCategories(false)
      }
    }
    loadCategories()
  }, [])

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    e.stopPropagation() // Empêcher la propagation au formulaire parent
    if (!newProduct.name.trim()) return

    try {
      const productData: any = {
        name: newProduct.name,
        description: newProduct.description,
        availability_type: newProduct.availability_type,
      }
      if (newProduct.category_id) productData.category_id = newProduct.category_id
      if (newProduct.availability_type === 'custom') {
        productData.availability_start_month = newProduct.availability_start_month
        productData.availability_end_month = newProduct.availability_end_month
      }
      await onCreate(productData)
      setNewProduct({
        name: '',
        description: '',
        category_id: undefined,
        availability_type: 'all_year',
        availability_start_month: null,
        availability_end_month: null,
      })
    } catch (error) {
      console.error('Error creating product:', error)
      // L'erreur sera gérée par le parent
    }
  }

  return (
    <div className="bg-white rounded-3xl shadow-nature-lg p-8 border-4 border-nature-200">
      <h2 className="text-2xl font-bold mb-6 text-nature-800 flex items-center gap-2">
        <span className="text-3xl">🌾</span>
        Produits
      </h2>

      <form onSubmit={handleAddProduct} onClick={(e) => e.stopPropagation()} className="mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nom du produit *
          </label>
          <input
            type="text"
            required
            value={newProduct.name}
            onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
            placeholder="Ex: Tomates"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Catégorie (optionnel)
          </label>
          {loadingCategories ? (
            <p className="text-gray-500 text-sm">Chargement des catégories...</p>
          ) : (
            <select
              value={newProduct.category_id || ''}
              onChange={(e) => setNewProduct({ ...newProduct, category_id: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
            >
              <option value="">Sélectionner une catégorie</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.display_name}
                </option>
              ))}
            </select>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description (optionnel)
          </label>
          <textarea
            value={newProduct.description}
            onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
            rows={2}
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-nature-50/30"
            placeholder="Description du produit"
          />
        </div>
        
        {/* Section Période de disponibilité - TOUJOURS VISIBLE */}
        <div className="border-t pt-4 mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            📅 Période de disponibilité
          </label>
          <select
            value={newProduct.availability_type}
            onChange={(e) => setNewProduct({
              ...newProduct,
              availability_type: e.target.value as 'all_year' | 'custom',
              availability_start_month: null,
              availability_end_month: null,
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 bg-white"
          >
            <option value="all_year">Tout l'année</option>
            <option value="custom">Période personnalisée</option>
          </select>
          
          {newProduct.availability_type === 'custom' && (
                 <div className="mt-4 grid grid-cols-2 gap-4 p-6 bg-gradient-to-br from-nature-50 to-nature-100 rounded-2xl border-2 border-nature-300">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mois de début *
                </label>
                <select
                  value={newProduct.availability_start_month || ''}
                  onChange={(e) => setNewProduct({
                    ...newProduct,
                    availability_start_month: e.target.value ? parseInt(e.target.value) : null,
                  })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 bg-white"
                >
                  <option value="">Sélectionner un mois</option>
                  {MONTHS.map((month) => (
                    <option key={month.value} value={month.value}>
                      {month.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mois de fin *
                </label>
                <select
                  value={newProduct.availability_end_month || ''}
                  onChange={(e) => setNewProduct({
                    ...newProduct,
                    availability_end_month: e.target.value ? parseInt(e.target.value) : null,
                  })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 bg-white"
                >
                  <option value="">Sélectionner un mois</option>
                  {MONTHS.map((month) => (
                    <option key={month.value} value={month.value}>
                      {month.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>
        
        <button
          type="submit"
                 className="w-full px-6 py-3 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl font-bold shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105"
        >
          Ajouter le produit
        </button>
      </form>

      {products.length > 0 ? (
        <div className="space-y-4 mt-6">
          {products.map((product) => (
            <ProductItem
              key={product.id}
              product={product}
              onEdit={(updatedProduct) => onUpdate(updatedProduct)}
              onDelete={() => onDelete(product.id)}
              onRefresh={onRefresh}
            />
          ))}
        </div>
      ) : (
        <p className="text-gray-500">Aucun produit ajouté pour le moment.</p>
      )}
    </div>
  )
}


