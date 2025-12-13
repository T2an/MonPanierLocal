'use client'

import { useEffect } from 'react'
import { configureLeafletIcons } from '@/lib/leaflet'

/**
 * Composant client pour configurer Leaflet une seule fois
 * Doit être inclus dans le layout
 */
export function LeafletConfig() {
  useEffect(() => {
    configureLeafletIcons()
  }, [])
  return null
}

