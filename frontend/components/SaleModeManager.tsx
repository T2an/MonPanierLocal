'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { OpeningStatusBadge } from '@/components/OpeningStatusBadge'
import { SingleModeSchedule } from '@/components/WeeklySchedule'
import type { SaleMode, OpeningHours, ProducerProfile } from '@/types'

interface SaleModeManagerProps {
  producer: ProducerProfile | null
  onRefresh: () => Promise<void>
}

const SALE_MODE_TYPES = [
  { value: 'on_site', label: 'Vente sur place / point de vente' },
  { value: 'phone_order', label: 'Commande par téléphone' },
  { value: 'vending_machine', label: 'Distributeur automatique' },
  { value: 'delivery', label: 'Livraison' },
  { value: 'market', label: 'Marchés' },
] as const

const SALE_MODE_HINTS: Record<string, string> = {
  on_site: 'Exemples : "vente à la ferme", "point de vente dédié", "à la criée sur le port"',
  phone_order: 'Exemples : "Appelez pour réserver votre panier", "Réservations possibles avant 18h"',
  vending_machine: 'Exemples : "Distributeur devant l\'exploitation", "Accessible 24/7", "Paiement CB uniquement"',
  delivery: 'Exemples : "Livraison dans un rayon de 15 km", "Livraison groupée le vendredi"',
  market: 'Exemples : "Présent au marché de Savenay le mercredi matin", "Marché de producteurs à Guérande le dimanche"',
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Lundi' },
  { value: 1, label: 'Mardi' },
  { value: 2, label: 'Mercredi' },
  { value: 3, label: 'Jeudi' },
  { value: 4, label: 'Vendredi' },
  { value: 5, label: 'Samedi' },
  { value: 6, label: 'Dimanche' },
]

export function SaleModeManager({ producer, onRefresh }: SaleModeManagerProps) {
  const [saleModes, setSaleModes] = useState<SaleMode[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [newMode, setNewMode] = useState<Partial<SaleMode> | null>(null)

  useEffect(() => {
    if (producer) {
      loadSaleModes()
    }
  }, [producer])

  const loadSaleModes = async () => {
    if (!producer) return
    try {
      setLoading(true)
      const modes = await apiClient.getSaleModes(producer.id)
      setSaleModes(modes)
    } catch (error) {
      console.error('Error loading sale modes:', error)
    } finally {
      setLoading(false)
    }
  }

  const initializeOpeningHours = (): OpeningHours[] => {
    return DAYS_OF_WEEK.map(day => ({
      day_of_week: day.value,
      is_closed: false,
      opening_time: '09:00',
      closing_time: '18:00',
    }))
  }

  const handleAddMode = () => {
    setNewMode({
      mode_type: 'on_site',
      title: '',
      instructions: '',
      opening_hours: initializeOpeningHours(),
      order: saleModes.length,
    })
  }

  const handleSaveNewMode = async () => {
    if (!producer || !newMode) return

    try {
      await apiClient.createSaleMode(producer.id, newMode)
      setNewMode(null)
      await loadSaleModes()
      await onRefresh()
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur lors de la création'
      alert(errorMessage)
    }
  }

  const handleUpdateMode = async (mode: SaleMode) => {
    if (!producer || !mode.id) return

    try {
      await apiClient.updateSaleMode(producer.id, mode.id, mode)
      setEditingId(null)
      await loadSaleModes()
      await onRefresh()
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur lors de la modification'
      alert(errorMessage)
    }
  }

  const handleDeleteMode = async (modeId: number) => {
    if (!producer || !confirm('Supprimer ce mode de vente ?')) return

    try {
      await apiClient.deleteSaleMode(producer.id, modeId)
      await loadSaleModes()
      await onRefresh()
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur lors de la suppression'
      alert(errorMessage)
    }
  }

  const renderModeForm = (mode: Partial<SaleMode>, isNew: boolean, onChange: (mode: Partial<SaleMode>) => void) => {
    const modeType = mode.mode_type || 'on_site'

    return (
      <div className="bg-gradient-to-br from-nature-50 to-nature-100 p-6 rounded-3xl space-y-5 border-4 border-nature-300">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Type de mode de vente *
          </label>
          <select
            value={modeType}
            onChange={(e) => onChange({
              ...mode,
              mode_type: e.target.value as SaleMode['mode_type'],
              // Reset fields when type changes
              phone_number: e.target.value === 'phone_order' ? mode.phone_number : undefined,
              is_24_7: e.target.value === 'vending_machine' ? mode.is_24_7 : false,
            })}
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
          >
            {SALE_MODE_TYPES.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500 italic">
            {SALE_MODE_HINTS[modeType]}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Titre *
          </label>
          <input
            type="text"
            required
            value={mode.title || ''}
            onChange={(e) => onChange({ ...mode, title: e.target.value })}
            placeholder={SALE_MODE_HINTS[modeType].split(',')[0].replace('Exemples : ', '')}
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Consigne obligatoire *
          </label>
          <textarea
            required
            value={mode.instructions || ''}
            onChange={(e) => onChange({ ...mode, instructions: e.target.value })}
            rows={2}
            placeholder="Ex: Merci d'appeler 1 jour à l'avance, Apportez vos contenants, Paiement uniquement en espèces"
            className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
          />
        </div>

        {/* Champs spécifiques selon le type */}
        {modeType === 'phone_order' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Numéro de téléphone * <span className="text-red-500">(obligatoire)</span>
            </label>
            <input
              type="tel"
              required
              value={mode.phone_number || ''}
              onChange={(e) => onChange({ ...mode, phone_number: e.target.value })}
              placeholder="06 12 34 56 78"
              className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
            />
          </div>
        )}

        {modeType === 'delivery' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Site web (optionnel)
              </label>
              <input
                type="url"
                value={mode.website_url || ''}
                onChange={(e) => onChange({ ...mode, website_url: e.target.value })}
                placeholder="https://example.com"
                className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Téléphone (optionnel)
              </label>
              <input
                type="tel"
                value={mode.phone_number || ''}
                onChange={(e) => onChange({ ...mode, phone_number: e.target.value })}
                placeholder="06 12 34 56 78"
                className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
              />
            </div>
          </>
        )}

        {modeType === 'vending_machine' && (
          <>
            <div className="flex items-center">
              <input
                type="checkbox"
                id={`24-7-${isNew ? 'new' : mode.id}`}
                checked={mode.is_24_7 || false}
                onChange={(e) => onChange({ ...mode, is_24_7: e.target.checked })}
                className="mr-2"
              />
              <label htmlFor={`24-7-${isNew ? 'new' : mode.id}`} className="text-sm font-medium text-gray-700">
                Disponible 24/7
              </label>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Adresse du distributeur (si différente)
              </label>
              <input
                type="text"
                value={mode.location_address || ''}
                onChange={(e) => onChange({ ...mode, location_address: e.target.value })}
                placeholder={producer?.address || 'Adresse'}
                className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
              />
            </div>
          </>
        )}

        {modeType === 'on_site' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Adresse (préremplie avec l'adresse principale)
            </label>
            <input
              type="text"
              value={mode.location_address || producer?.address || ''}
              onChange={(e) => onChange({ ...mode, location_address: e.target.value })}
              className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
            />
          </div>
        )}

        {modeType === 'market' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Indications marché (jours, horaires, lieux)
            </label>
            <textarea
              value={mode.market_info || ''}
              onChange={(e) => onChange({ ...mode, market_info: e.target.value })}
              rows={3}
              placeholder="Ex: Présent au marché de Savenay le mercredi matin de 8h à 12h, Marché de producteurs à Guérande le dimanche de 9h à 13h"
              className="w-full px-4 py-3 border-2 border-nature-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-nature-400 focus:border-nature-500 transition-all bg-white"
            />
          </div>
        )}

        {/* Horaires d'ouverture */}
        {(modeType !== 'vending_machine' || !mode.is_24_7) && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Horaires d'ouverture
            </label>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {mode.opening_hours?.map((hours, index) => (
                <div key={hours.day_of_week} className="flex items-center gap-3 bg-white p-4 rounded-2xl border-2 border-nature-200 shadow-sm">
                  <div className="w-24 text-sm font-medium">
                    {DAYS_OF_WEEK.find(d => d.value === hours.day_of_week)?.label}
                  </div>
                  <input
                    type="checkbox"
                    checked={hours.is_closed}
                    onChange={(e) => {
                      const newHours = [...(mode.opening_hours || [])]
                      newHours[index] = { ...hours, is_closed: e.target.checked, opening_time: e.target.checked ? null : (hours.opening_time || '09:00'), closing_time: e.target.checked ? null : (hours.closing_time || '18:00') }
                      onChange({ ...mode, opening_hours: newHours })
                    }}
                    className="mr-2"
                  />
                  <label className="text-sm text-gray-600">Fermé</label>
                  {!hours.is_closed && (
                    <>
                      <input
                        type="time"
                        value={hours.opening_time || '09:00'}
                        onChange={(e) => {
                          const newHours = [...(mode.opening_hours || [])]
                          newHours[index] = { ...hours, opening_time: e.target.value }
                          onChange({ ...mode, opening_hours: newHours })
                        }}
                        className="px-3 py-1.5 border-2 border-nature-300 rounded-xl text-sm font-medium bg-white"
                      />
                      <span className="text-gray-600">à</span>
                      <input
                        type="time"
                        value={hours.closing_time || '18:00'}
                        onChange={(e) => {
                          const newHours = [...(mode.opening_hours || [])]
                          newHours[index] = { ...hours, closing_time: e.target.value }
                          onChange({ ...mode, opening_hours: newHours })
                        }}
                        className="px-3 py-1.5 border-2 border-nature-300 rounded-xl text-sm font-medium bg-white"
                      />
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-3 pt-4 border-t-2 border-nature-300">
          <button
            type="button"
            onClick={() => {
              if (isNew) {
                handleSaveNewMode()
              } else if (mode.id) {
                handleUpdateMode(mode as SaleMode)
              }
            }}
            disabled={
              !mode.title || 
              !mode.instructions || 
              (modeType === 'phone_order' && !mode.phone_number)
            }
            className="px-6 py-3 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl font-bold shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {isNew ? 'Ajouter' : 'Enregistrer'}
          </button>
          <button
            type="button"
            onClick={() => {
              if (isNew) {
                setNewMode(null)
              } else {
                setEditingId(null)
                // Recharger les modes depuis le serveur
                loadSaleModes()
              }
            }}
            className="px-6 py-3 bg-earth-100 hover:bg-earth-200 text-earth-800 rounded-2xl font-medium border-2 border-earth-300 transition-all"
          >
            Annuler
          </button>
        </div>
      </div>
    )
  }

  if (!producer) {
    return (
      <div className="bg-white rounded-3xl shadow-nature-lg p-8 border-4 border-nature-200">
        <p className="text-gray-500">Créez d'abord votre profil producteur pour ajouter des modes de vente.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="bg-white rounded-3xl shadow-nature-lg p-8 border-4 border-nature-200">
        <p className="text-gray-500">Chargement...</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Modes de vente</h2>
        {!newMode && (
          <button
            type="button"
            onClick={handleAddMode}
            className="px-6 py-3 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl font-bold shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105"
          >
            + Ajouter un mode de vente
          </button>
        )}
      </div>

      {newMode && renderModeForm(newMode, true, setNewMode)}

      {saleModes.length === 0 && !newMode && (
        <p className="text-gray-500">Aucun mode de vente ajouté pour le moment.</p>
      )}

      {saleModes.map((mode) => (
        <div key={mode.id} className="border-4 border-nature-200 rounded-3xl p-6 bg-gradient-to-br from-white to-nature-50/30 shadow-nature mb-6">
          {editingId === mode.id ? (
            renderModeForm(mode, false, (updated) => {
              const index = saleModes.findIndex(m => m.id === mode.id)
              const newModes = [...saleModes]
              newModes[index] = { ...mode, ...updated } as SaleMode
              setSaleModes(newModes)
            })
          ) : (
            <>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex flex-wrap items-start gap-3 mb-2">
                    <div>
                      <h3 className="font-semibold text-lg">{mode.title}</h3>
                      <p className="text-sm text-gray-600">{mode.mode_type_display || mode.mode_type}</p>
                    </div>
                    {/* Badge de statut d'ouverture en temps réel */}
                    <OpeningStatusBadge 
                      openingHours={mode.opening_hours} 
                      is24_7={mode.is_24_7}
                    />
                  </div>
                  <p className="text-sm text-gray-700 mt-2">
                    <strong>Consigne:</strong> {mode.instructions}
                  </p>
                  {mode.phone_number && (
                    <p className="text-sm text-gray-600 mt-1">📞 {mode.phone_number}</p>
                  )}
                  {mode.website_url && (
                    <p className="text-sm text-gray-600 mt-1">🌐 <a href={mode.website_url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">{mode.website_url}</a></p>
                  )}
                  {mode.market_info && (
                    <p className="text-sm text-gray-600 mt-1">{mode.market_info}</p>
                  )}
                  {/* Semainier visuel */}
                  {(mode.opening_hours && mode.opening_hours.length > 0) || mode.is_24_7 ? (
                    <div className="mt-3 p-3 bg-white rounded-xl border-2 border-nature-200">
                      <p className="text-sm font-medium text-gray-700 mb-2">Disponibilités :</p>
                      <SingleModeSchedule 
                        openingHours={mode.opening_hours} 
                        is24_7={mode.is_24_7} 
                      />
                    </div>
                  ) : null}
                </div>
                <div className="flex gap-2 ml-4">
                  <button
                    type="button"
                    onClick={() => setEditingId(mode.id || null)}
                    className="px-5 py-2 bg-nature-500 hover:bg-nature-600 text-white rounded-2xl text-sm font-semibold shadow-nature hover:shadow-nature-lg transition-all transform hover:scale-105"
                  >
                    Modifier
                  </button>
                  <button
                    type="button"
                    onClick={() => mode.id && handleDeleteMode(mode.id)}
                    className="px-5 py-2 bg-red-500 hover:bg-red-600 text-white rounded-2xl text-sm font-semibold shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
                  >
                    Supprimer
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  )
}

