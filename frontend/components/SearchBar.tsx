'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { createPortal } from 'react-dom'
import { apiClient } from '@/lib/api'
import type { ProducerProfile } from '@/types'

interface SearchBarProps {
  onProducerSelect?: (producer: ProducerProfile | null) => void
}

export function SearchBar({ onProducerSelect }: SearchBarProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [searchTerm, setSearchTerm] = useState('')
  const [suggestions, setSuggestions] = useState<ProducerProfile[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedProducer, setSelectedProducer] = useState<ProducerProfile | null>(null)
  const [dropdownRect, setDropdownRect] = useState<{ top: number; left: number; width: number } | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    const query = searchParams.get('q') || ''
    setSearchTerm(query)
  }, [searchParams])

  const updateDropdownPosition = useCallback(() => {
    if (!inputRef.current) return
    const rect = inputRef.current.getBoundingClientRect()
    setDropdownRect({
      top: rect.bottom + window.scrollY,
      left: rect.left + window.scrollX,
      width: rect.width,
    })
  }, [])

  const searchProducers = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setSuggestions([])
      return
    }

    setIsLoading(true)
    try {
      const data = await apiClient.getProducers({ search: query })
      const results = data.results || []
      // Limiter à 10 résultats pour l'autocomplétion
      setSuggestions(results.slice(0, 10))
      updateDropdownPosition()
    } catch (err) {
      setSuggestions([])
    } finally {
      setIsLoading(false)
    }
  }, [updateDropdownPosition])

  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }

    if (searchTerm.trim().length >= 2 && !selectedProducer) {
      searchTimeoutRef.current = setTimeout(() => {
        searchProducers(searchTerm)
      }, 300)
    } else {
      setSuggestions([])
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [searchTerm, searchProducers, selectedProducer])

  useEffect(() => {
    updateDropdownPosition()
    const handleResize = () => updateDropdownPosition()
    const handleScroll = () => updateDropdownPosition()
    
    window.addEventListener('resize', handleResize)
    window.addEventListener('scroll', handleScroll, true)
    
    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('scroll', handleScroll, true)
    }
  }, [updateDropdownPosition, showSuggestions])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleSelect = (producer: ProducerProfile) => {
    setSelectedProducer(producer)
    setSearchTerm(producer.name)
    setShowSuggestions(false)
    setSuggestions([])
    if (onProducerSelect) {
      onProducerSelect(producer)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setShowSuggestions(false)
    
    if (selectedProducer) {
      // Si un producteur est sélectionné, on utilise son ID
      if (onProducerSelect) {
        onProducerSelect(selectedProducer)
      }
    } else if (searchTerm.trim()) {
      // Recherche par nom : chercher le premier producteur correspondant
      try {
        const data = await apiClient.getProducers({ search: searchTerm.trim() })
        const results = data.results || []
        if (results.length > 0) {
          // Prendre le premier résultat
          const firstProducer = results[0]
          setSelectedProducer(firstProducer)
          if (onProducerSelect) {
            onProducerSelect(firstProducer)
          }
        } else {
          // Aucun résultat trouvé, on peut quand même notifier le parent
          if (onProducerSelect) {
            onProducerSelect(null)
          }
        }
      } catch (err) {
        // En cas d'erreur, notifier le parent
        if (onProducerSelect) {
          onProducerSelect(null)
        }
      }
    } else {
      // Champ vide, effacer la sélection
      if (onProducerSelect) {
        onProducerSelect(null)
      }
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchTerm(value)
    setSelectedProducer(null)
    setShowSuggestions(true)
    if (onProducerSelect) {
      onProducerSelect(null)
    }
  }

  // Grouper les producteurs par nom pour afficher l'adresse si plusieurs
  const groupedProducers = suggestions.reduce((acc, producer) => {
    if (!acc[producer.name]) {
      acc[producer.name] = []
    }
    acc[producer.name].push(producer)
    return acc
  }, {} as Record<string, ProducerProfile[]>)

  return (
    <form onSubmit={handleSearch} className="w-full">
      <div className="flex gap-2 items-center">
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            value={searchTerm}
            onChange={handleInputChange}
            onFocus={() => {
              setShowSuggestions(true)
              updateDropdownPosition()
            }}
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
        <button
          type="submit"
          aria-label="Lancer la recherche"
          className="px-4 py-3 rounded-2xl text-sm font-bold text-white bg-green-500 hover:bg-green-600 active:bg-green-700 shadow-nature transition-all whitespace-nowrap"
        >
          GO
        </button>
      </div>

      {showSuggestions && suggestions.length > 0 && dropdownRect && typeof document !== 'undefined' &&
        createPortal(
          <div
            ref={suggestionsRef}
            style={{
              position: 'absolute',
              top: dropdownRect.top,
              left: dropdownRect.left,
              width: dropdownRect.width,
            }}
            className="z-[2000] mt-1 bg-white border-2 border-nature-200 rounded-2xl shadow-nature-lg overflow-hidden"
          >
            {isLoading && (
              <div className="px-4 py-3 text-sm text-gray-500 text-center">
                Recherche en cours...
              </div>
            )}
            {Object.entries(groupedProducers).map(([name, producers]) => (
              <div key={name}>
                {producers.map((producer, index) => (
                  <button
                    key={producer.id}
                    type="button"
                    onClick={() => handleSelect(producer)}
                    className="w-full text-left px-4 py-3 hover:bg-nature-50 transition-colors border-b border-nature-100 last:border-b-0"
                  >
                    <div className="font-semibold text-earth-700">{producer.name}</div>
                    {producers.length > 1 && (
                      <div className="text-xs text-gray-500 mt-1">{producer.address}</div>
                    )}
                  </button>
                ))}
              </div>
            ))}
          </div>,
          document.body
        )
      }
    </form>
  )
}

