'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export function SearchBar() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    // Lire le terme de recherche depuis l'URL
    const query = searchParams.get('q') || ''
    setSearchTerm(query)
  }, [searchParams])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const category = searchParams.get('category')
    const params = new URLSearchParams()
    if (searchTerm.trim()) {
      params.set('q', searchTerm.trim())
    }
    if (category) {
      params.set('category', category)
    }
    const queryString = params.toString()
    router.push(queryString ? `/?${queryString}` : '/')
  }

  return (
    <form onSubmit={handleSearch} className="flex-1 max-w-md">
      <div className="relative">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Rechercher un producteur..."
          className="w-full px-5 py-3 pl-12 pr-5 text-earth-700 bg-white border-3 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 shadow-nature transition-all"
        />
        <div className="absolute inset-y-0 left-0 flex items-center pl-3">
          <svg
            className="w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>
    </form>
  )
}

