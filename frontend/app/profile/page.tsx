'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorMessage } from '@/components/ErrorMessage'
import Link from 'next/link'

export default function ProfilePage() {
  const { user, loading, refreshUser } = useAuth()
  const router = useRouter()
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({
    email: '',
    username: '',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  })
  const [changingPassword, setChangingPassword] = useState(false)

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    } else if (user) {
      setEditData({
        email: user.email,
        username: user.username,
      })
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-lg text-gray-600">Chargement...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      await apiClient.updateMe(editData)
      await refreshUser()
      setIsEditing(false)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la modification'
      setError(errorMessage)
    } finally {
      setSaving(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setChangingPassword(true)
    setError(null)
    try {
      await apiClient.changePassword(passwordData)
      setShowPasswordForm(false)
      setPasswordData({
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      })
      alert('Mot de passe modifié avec succès')
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors du changement de mot de passe'
      setError(errorMessage)
    } finally {
      setChangingPassword(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Mon Profil</h1>
      
      {error && <ErrorMessage message={error} className="mb-6" />}

      <div className="bg-white rounded-lg shadow-lg p-6">
        {!isEditing ? (
          <>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <p className="mt-1 text-gray-900">{user.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Nom d'utilisateur</label>
                <p className="mt-1 text-gray-900">{user.username}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Type de compte</label>
                <p className="mt-1 text-gray-900">
                  {user.is_producer ? 'Producteur' : 'Utilisateur'}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Date d'inscription</label>
                <p className="mt-1 text-gray-900">
                  {new Date(user.date_joined).toLocaleDateString('fr-FR')}
                </p>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t flex gap-4">
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md"
              >
                Modifier mon profil
              </button>
              <button
                onClick={() => setShowPasswordForm(!showPasswordForm)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md"
              >
                Changer le mot de passe
              </button>
              {user.is_producer && (
                <Link
                  href="/producer/edit"
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md inline-block"
                >
                  Gérer mon exploitation
                </Link>
              )}
            </div>
          </>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                type="email"
                required
                value={editData.email}
                onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nom d'utilisateur *</label>
              <input
                type="text"
                required
                value={editData.username}
                onChange={(e) => setEditData({ ...editData, username: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500"
              />
            </div>
            <div className="flex gap-4">
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50"
              >
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
              <button
                onClick={() => {
                  setIsEditing(false)
                  setEditData({ email: user.email, username: user.username })
                }}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md"
              >
                Annuler
              </button>
            </div>
          </div>
        )}

        {showPasswordForm && (
          <div className="mt-6 pt-6 border-t">
            <h2 className="text-xl font-semibold mb-4">Changer le mot de passe</h2>
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ancien mot de passe *
                </label>
                <input
                  type="password"
                  required
                  value={passwordData.old_password}
                  onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nouveau mot de passe *
                </label>
                <input
                  type="password"
                  required
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirmer le nouveau mot de passe *
                </label>
                <input
                  type="password"
                  required
                  value={passwordData.new_password_confirm}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password_confirm: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500"
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={changingPassword}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50"
                >
                  {changingPassword ? 'Modification...' : 'Modifier le mot de passe'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordForm(false)
                    setPasswordData({
                      old_password: '',
                      new_password: '',
                      new_password_confirm: '',
                    })
                  }}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  )
}

