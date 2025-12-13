'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ErrorMessage } from '@/components/ErrorMessage'
import { LoadingSpinner } from '@/components/LoadingSpinner'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    // Pour l'instant, on simule l'envoi
    // Dans une vraie app, on appellerait l'API
    setTimeout(() => {
      setLoading(false)
      setSuccess(true)
      setFormData({ name: '', email: '', subject: '', message: '' })
    }, 1000)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link
        href="/"
        className="text-primary-600 hover:text-primary-700 mb-4 inline-block"
      >
        ← Retour à l'accueil
      </Link>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-4xl font-bold mb-6">Contactez-nous</h1>

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.
          </div>
        )}

        {error && <ErrorMessage message={error} className="mb-6" />}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Nom *
            </label>
            <input
              type="text"
              id="name"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              id="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
              Sujet *
            </label>
            <input
              type="text"
              id="subject"
              required
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
              Message *
            </label>
            <textarea
              id="message"
              required
              rows={6}
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Envoi en cours...
              </>
            ) : (
              'Envoyer le message'
            )}
          </button>
        </form>

        <div className="mt-8 pt-8 border-t">
          <h2 className="text-xl font-semibold mb-4">Autres moyens de contact</h2>
          <div className="space-y-2 text-gray-700">
            <p>📧 Email : contact@monpanierlocal.fr</p>
            <p>📞 Téléphone : 01 23 45 67 89</p>
            <p>📍 Adresse : 123 Rue de l'Agriculture, 75001 Paris</p>
          </div>
        </div>
      </div>
    </div>
  )
}

