'use client'

import { useMemo } from 'react'
import type { SaleMode, OpeningHours } from '@/types'

interface WeeklyScheduleProps {
  saleModes: SaleMode[]
  compact?: boolean
}

const DAYS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
const DAYS_FULL = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

// Palette de couleurs pour les différents modes de vente
const MODE_COLORS = [
  { bg: 'bg-emerald-500', text: 'text-emerald-700', light: 'bg-emerald-100', border: 'border-emerald-300' },
  { bg: 'bg-blue-500', text: 'text-blue-700', light: 'bg-blue-100', border: 'border-blue-300' },
  { bg: 'bg-amber-500', text: 'text-amber-700', light: 'bg-amber-100', border: 'border-amber-300' },
  { bg: 'bg-purple-500', text: 'text-purple-700', light: 'bg-purple-100', border: 'border-purple-300' },
  { bg: 'bg-rose-500', text: 'text-rose-700', light: 'bg-rose-100', border: 'border-rose-300' },
  { bg: 'bg-cyan-500', text: 'text-cyan-700', light: 'bg-cyan-100', border: 'border-cyan-300' },
]

const MODE_ICONS: Record<string, string> = {
  'on_site': '🏪',
  'phone_order': '📞',
  'vending_machine': '🤖',
  'delivery': '🚚',
  'market': '🛒',
}

interface TimeSlot {
  modeIndex: number
  modeTitle: string
  modeType: string
  startMinutes: number
  endMinutes: number
  is24_7: boolean
}

function parseTime(time: string | null): number {
  if (!time) return 0
  const [hours, minutes] = time.split(':').map(Number)
  return hours * 60 + minutes
}

function formatTime(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h}h${m.toString().padStart(2, '0')}`
}

function getCurrentDayIndex(): number {
  const jsDay = new Date().getDay()
  return jsDay === 0 ? 6 : jsDay - 1
}

export function WeeklySchedule({ saleModes, compact = false }: WeeklyScheduleProps) {
  const currentDay = getCurrentDayIndex()
  
  // Préparer les données par jour
  const scheduleByDay = useMemo(() => {
    const result: TimeSlot[][] = Array.from({ length: 7 }, () => [])
    
    saleModes.forEach((mode, modeIndex) => {
      if (mode.is_24_7) {
        // 24/7 - disponible tous les jours
        for (let day = 0; day < 7; day++) {
          result[day].push({
            modeIndex,
            modeTitle: mode.title,
            modeType: mode.mode_type,
            startMinutes: 0,
            endMinutes: 24 * 60,
            is24_7: true,
          })
        }
      } else if (mode.opening_hours) {
        mode.opening_hours.forEach((hours) => {
          if (!hours.is_closed && hours.opening_time && hours.closing_time) {
            result[hours.day_of_week].push({
              modeIndex,
              modeTitle: mode.title,
              modeType: mode.mode_type,
              startMinutes: parseTime(hours.opening_time),
              endMinutes: parseTime(hours.closing_time),
              is24_7: false,
            })
          }
        })
      }
    })
    
    return result
  }, [saleModes])
  
  // Trouver les heures min et max pour l'affichage
  const { minHour, maxHour } = useMemo(() => {
    let min = 24
    let max = 0
    
    scheduleByDay.forEach(daySlots => {
      daySlots.forEach(slot => {
        if (slot.is24_7) {
          min = 0
          max = 24
        } else {
          const startHour = Math.floor(slot.startMinutes / 60)
          const endHour = Math.ceil(slot.endMinutes / 60)
          min = Math.min(min, startHour)
          max = Math.max(max, endHour)
        }
      })
    })
    
    // Valeurs par défaut si pas de créneaux
    if (min === 24) min = 8
    if (max === 0) max = 20
    
    // Arrondir pour un affichage plus propre
    min = Math.max(0, min - 1)
    max = Math.min(24, max + 1)
    
    return { minHour: min, maxHour: max }
  }, [scheduleByDay])
  
  const totalHours = maxHour - minHour
  const hourHeight = compact ? 16 : 24 // pixels par heure
  
  if (saleModes.length === 0) {
    return (
      <div className="p-4 bg-gray-50 rounded-xl text-gray-500 text-center">
        Aucun mode de vente configuré
      </div>
    )
  }
  
  return (
    <div className="bg-white rounded-2xl border-2 border-nature-200 overflow-hidden">
      {/* Légende */}
      <div className="p-3 bg-gradient-to-r from-nature-50 to-white border-b-2 border-nature-100">
        <div className="flex flex-wrap gap-2">
          {saleModes.map((mode, index) => {
            const color = MODE_COLORS[index % MODE_COLORS.length]
            return (
              <div
                key={mode.id || index}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${color.light} ${color.text} ${color.border} border`}
              >
                <span>{MODE_ICONS[mode.mode_type] || '📍'}</span>
                <span className="truncate max-w-[120px]">{mode.title}</span>
                {mode.is_24_7 && <span className="text-[10px]">24/7</span>}
              </div>
            )
          })}
        </div>
      </div>
      
      {/* Grille du semainier */}
      <div className="flex">
        {/* Colonne des heures */}
        <div className="flex-shrink-0 w-12 bg-gray-50 border-r border-gray-200">
          <div className="h-8 border-b border-gray-200"></div>
          <div className="relative" style={{ height: `${totalHours * hourHeight}px` }}>
            {Array.from({ length: totalHours + 1 }).map((_, i) => {
              const hour = minHour + i
              if (hour > maxHour) return null
              return (
                <div
                  key={hour}
                  className="absolute w-full text-[10px] text-gray-500 text-right pr-1 -translate-y-1/2"
                  style={{ top: `${i * hourHeight}px` }}
                >
                  {hour}h
                </div>
              )
            })}
          </div>
        </div>
        
        {/* Colonnes des jours */}
        <div className="flex-1 grid grid-cols-7">
          {DAYS.map((day, dayIndex) => {
            const isToday = dayIndex === currentDay
            const daySlots = scheduleByDay[dayIndex]
            
            return (
              <div
                key={day}
                className={`border-r border-gray-100 last:border-r-0 ${isToday ? 'bg-nature-50/50' : ''}`}
              >
                {/* En-tête du jour */}
                <div
                  className={`h-8 flex items-center justify-center text-xs font-semibold border-b border-gray-200 ${
                    isToday ? 'bg-nature-500 text-white' : 'bg-gray-50 text-gray-700'
                  }`}
                >
                  {day}
                </div>
                
                {/* Zone des créneaux */}
                <div
                  className="relative"
                  style={{ height: `${totalHours * hourHeight}px` }}
                >
                  {/* Lignes des heures */}
                  {Array.from({ length: totalHours }).map((_, i) => (
                    <div
                      key={i}
                      className="absolute w-full border-t border-gray-100"
                      style={{ top: `${i * hourHeight}px` }}
                    />
                  ))}
                  
                  {/* Créneaux */}
                  {daySlots.map((slot, slotIndex) => {
                    const color = MODE_COLORS[slot.modeIndex % MODE_COLORS.length]
                    const startOffset = slot.is24_7 
                      ? 0 
                      : ((slot.startMinutes / 60) - minHour) * hourHeight
                    const height = slot.is24_7
                      ? totalHours * hourHeight
                      : ((slot.endMinutes - slot.startMinutes) / 60) * hourHeight
                    
                    // Décaler légèrement si plusieurs créneaux se chevauchent
                    const leftOffset = slotIndex * 2
                    const rightOffset = (daySlots.length - 1 - slotIndex) * 2
                    
                    return (
                      <div
                        key={`${slot.modeIndex}-${slotIndex}`}
                        className={`absolute ${color.bg} opacity-80 hover:opacity-100 transition-opacity cursor-pointer rounded-sm`}
                        style={{
                          top: `${startOffset}px`,
                          height: `${Math.max(height, 8)}px`,
                          left: `${1 + leftOffset}px`,
                          right: `${1 + rightOffset}px`,
                        }}
                        title={`${slot.modeTitle}\n${slot.is24_7 ? '24h/24' : `${formatTime(slot.startMinutes)} - ${formatTime(slot.endMinutes)}`}`}
                      >
                        {height >= 20 && (
                          <div className="text-white text-[8px] font-medium truncate px-0.5 pt-0.5">
                            {MODE_ICONS[slot.modeType]}
                          </div>
                        )}
                      </div>
                    )
                  })}
                  
                  {/* Indicateur "Fermé" si aucun créneau */}
                  {daySlots.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-[10px] text-gray-400 font-medium">Fermé</span>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
      
      {/* Indicateur jour actuel */}
      <div className="p-2 bg-gray-50 border-t border-gray-200 text-center">
        <span className="text-xs text-gray-500">
          Aujourd'hui : <span className="font-medium text-nature-700">{DAYS_FULL[currentDay]}</span>
        </span>
      </div>
    </div>
  )
}

// Version simplifiée pour un seul mode de vente
export function SingleModeSchedule({ openingHours, is24_7 }: { openingHours?: OpeningHours[], is24_7?: boolean }) {
  if (is24_7) {
    return (
      <div className="flex gap-1 items-center">
        {DAYS.map((day, index) => (
          <div
            key={day}
            className={`flex-1 h-8 rounded-lg flex items-center justify-center text-xs font-medium bg-emerald-500 text-white ${
              index === getCurrentDayIndex() ? 'ring-2 ring-emerald-300 ring-offset-1' : ''
            }`}
            title={`${DAYS_FULL[index]} : 24h/24`}
          >
            {day}
          </div>
        ))}
      </div>
    )
  }
  
  if (!openingHours || openingHours.length === 0) {
    return (
      <div className="text-sm text-gray-500">Horaires non définis</div>
    )
  }
  
  const currentDay = getCurrentDayIndex()
  
  return (
    <div className="space-y-1">
      <div className="flex gap-1">
        {DAYS.map((day, dayIndex) => {
          const schedule = openingHours.find(h => h.day_of_week === dayIndex)
          const isOpen = schedule && !schedule.is_closed && schedule.opening_time
          const isToday = dayIndex === currentDay
          
          return (
            <div
              key={day}
              className={`flex-1 h-10 rounded-lg flex flex-col items-center justify-center text-xs font-medium transition-all ${
                isOpen 
                  ? 'bg-emerald-500 text-white' 
                  : 'bg-gray-200 text-gray-500'
              } ${isToday ? 'ring-2 ring-nature-400 ring-offset-1 scale-105' : ''}`}
              title={
                schedule 
                  ? schedule.is_closed 
                    ? `${DAYS_FULL[dayIndex]} : Fermé`
                    : `${DAYS_FULL[dayIndex]} : ${schedule.opening_time?.substring(0, 5)} - ${schedule.closing_time?.substring(0, 5)}`
                  : `${DAYS_FULL[dayIndex]} : Non défini`
              }
            >
              <span className={isToday ? 'font-bold' : ''}>{day}</span>
              {isOpen && schedule?.opening_time && (
                <span className="text-[9px] opacity-90">
                  {schedule.opening_time.substring(0, 5)}
                </span>
              )}
            </div>
          )
        })}
      </div>
      
      {/* Afficher les détails du jour actuel */}
      {(() => {
        const todaySchedule = openingHours.find(h => h.day_of_week === currentDay)
        if (todaySchedule && !todaySchedule.is_closed && todaySchedule.opening_time && todaySchedule.closing_time) {
          return (
            <p className="text-xs text-center text-gray-600 mt-1">
              Aujourd'hui : <span className="font-medium text-nature-700">
                {todaySchedule.opening_time.substring(0, 5)} - {todaySchedule.closing_time.substring(0, 5)}
              </span>
            </p>
          )
        } else if (todaySchedule?.is_closed) {
          return (
            <p className="text-xs text-center text-gray-500 mt-1">
              Fermé aujourd'hui
            </p>
          )
        }
        return null
      })()}
    </div>
  )
}




