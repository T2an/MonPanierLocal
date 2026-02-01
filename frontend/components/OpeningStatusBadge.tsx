'use client'

import { useMemo } from 'react'
import type { OpeningHours } from '@/types'

interface OpeningStatusBadgeProps {
  openingHours?: OpeningHours[]
  is24_7?: boolean
  className?: string
  showDetails?: boolean
}

interface OpeningStatus {
  isOpen: boolean
  is24_7: boolean
  closesIn?: string
  opensIn?: string
  nextOpening?: { day: string; time: string }
  todayHours?: { open: string; close: string }
}

const DAYS_NAMES = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

function getOpeningStatus(openingHours?: OpeningHours[], is24_7?: boolean): OpeningStatus {
  if (is24_7) {
    return { isOpen: true, is24_7: true }
  }

  if (!openingHours || openingHours.length === 0) {
    return { isOpen: false, is24_7: false }
  }

  const now = new Date()
  // JavaScript: 0 = Dimanche, 1 = Lundi, ..., 6 = Samedi
  // Notre modèle: 0 = Lundi, 1 = Mardi, ..., 6 = Dimanche
  const jsDay = now.getDay()
  const currentDay = jsDay === 0 ? 6 : jsDay - 1
  const currentTime = now.getHours() * 60 + now.getMinutes()

  // Trouver les horaires d'aujourd'hui
  const todaySchedule = openingHours.find(h => h.day_of_week === currentDay)
  
  if (todaySchedule && !todaySchedule.is_closed && todaySchedule.opening_time && todaySchedule.closing_time) {
    const [openHour, openMin] = todaySchedule.opening_time.split(':').map(Number)
    const [closeHour, closeMin] = todaySchedule.closing_time.split(':').map(Number)
    const openTime = openHour * 60 + openMin
    const closeTime = closeHour * 60 + closeMin

    // Actuellement ouvert
    if (currentTime >= openTime && currentTime < closeTime) {
      const minutesUntilClose = closeTime - currentTime
      return {
        isOpen: true,
        is24_7: false,
        closesIn: formatDuration(minutesUntilClose),
        todayHours: {
          open: todaySchedule.opening_time,
          close: todaySchedule.closing_time
        }
      }
    }

    // Pas encore ouvert aujourd'hui
    if (currentTime < openTime) {
      const minutesUntilOpen = openTime - currentTime
      return {
        isOpen: false,
        is24_7: false,
        opensIn: formatDuration(minutesUntilOpen),
        todayHours: {
          open: todaySchedule.opening_time,
          close: todaySchedule.closing_time
        }
      }
    }
  }

  // Fermé aujourd'hui ou déjà passé - chercher la prochaine ouverture
  const nextOpening = findNextOpening(openingHours, currentDay, currentTime)
  
  return {
    isOpen: false,
    is24_7: false,
    nextOpening
  }
}

function findNextOpening(
  openingHours: OpeningHours[], 
  currentDay: number, 
  currentTime: number
): { day: string; time: string } | undefined {
  // Chercher dans les 7 prochains jours
  for (let i = 0; i < 7; i++) {
    const checkDay = (currentDay + i) % 7
    const schedule = openingHours.find(h => h.day_of_week === checkDay)
    
    if (schedule && !schedule.is_closed && schedule.opening_time) {
      const [openHour, openMin] = schedule.opening_time.split(':').map(Number)
      const openTime = openHour * 60 + openMin
      
      // Si c'est aujourd'hui, vérifier que l'heure n'est pas passée
      if (i === 0 && openTime <= currentTime) {
        continue
      }
      
      let dayLabel: string
      if (i === 0) {
        dayLabel = "Aujourd'hui"
      } else if (i === 1) {
        dayLabel = 'Demain'
      } else {
        dayLabel = DAYS_NAMES[checkDay]
      }
      
      return {
        day: dayLabel,
        time: schedule.opening_time.substring(0, 5)
      }
    }
  }
  
  return undefined
}

function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} min`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (mins === 0) {
    return `${hours}h`
  }
  return `${hours}h${mins.toString().padStart(2, '0')}`
}

export function OpeningStatusBadge({ 
  openingHours, 
  is24_7, 
  className = '',
  showDetails = true 
}: OpeningStatusBadgeProps) {
  const status = useMemo(() => getOpeningStatus(openingHours, is24_7), [openingHours, is24_7])

  if (status.is24_7) {
    return (
      <div className={`inline-flex items-center gap-2 ${className}`}>
        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-100 text-emerald-800 rounded-full text-sm font-semibold">
          <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
          Ouvert 24h/24
        </span>
      </div>
    )
  }

  if (status.isOpen) {
    return (
      <div className={`flex flex-col gap-1 ${className}`}>
        <div className="inline-flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-100 text-emerald-800 rounded-full text-sm font-semibold">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            Ouvert
          </span>
          {showDetails && status.closesIn && (
            <span className="text-sm text-gray-600">
              Ferme dans {status.closesIn}
            </span>
          )}
        </div>
        {showDetails && status.todayHours && (
          <span className="text-xs text-gray-500">
            Aujourd'hui : {status.todayHours.open.substring(0, 5)} - {status.todayHours.close.substring(0, 5)}
          </span>
        )}
      </div>
    )
  }

  // Fermé
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <div className="inline-flex items-center gap-2">
        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
          <span className="w-2 h-2 bg-red-500 rounded-full"></span>
          Fermé
        </span>
        {showDetails && status.opensIn && (
          <span className="text-sm text-emerald-600 font-medium">
            ⏰ Ouvre dans {status.opensIn}
          </span>
        )}
      </div>
      {showDetails && status.nextOpening && !status.opensIn && (
        <span className="text-sm text-gray-600">
          Prochaine ouverture : <span className="font-medium text-nature-700">{status.nextOpening.day} à {status.nextOpening.time}</span>
        </span>
      )}
      {showDetails && status.todayHours && (
        <span className="text-xs text-gray-500">
          Aujourd'hui : {status.todayHours.open.substring(0, 5)} - {status.todayHours.close.substring(0, 5)}
        </span>
      )}
    </div>
  )
}

// Version compacte pour les listes
export function OpeningStatusDot({ 
  openingHours, 
  is24_7 
}: { 
  openingHours?: OpeningHours[]
  is24_7?: boolean 
}) {
  const status = useMemo(() => getOpeningStatus(openingHours, is24_7), [openingHours, is24_7])

  if (status.is24_7 || status.isOpen) {
    return (
      <span className="inline-flex items-center gap-1 text-emerald-600" title="Ouvert maintenant">
        <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
        <span className="text-xs font-medium">Ouvert</span>
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-1 text-red-600" title="Fermé">
      <span className="w-2 h-2 bg-red-500 rounded-full"></span>
      <span className="text-xs font-medium">Fermé</span>
    </span>
  )
}




