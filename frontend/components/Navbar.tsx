'use client'

import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'

export function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="bg-white border-b-4 border-nature-300 shadow-nature">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20">
          <div className="flex items-center">
            <Link href="/" className="text-3xl font-bold text-nature-700 hover:text-nature-600 transition-colors flex items-center gap-2">
              <span className="text-4xl">🌾</span>
              <span>Mon Panier Local</span>
            </Link>
          </div>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <Link
                  href="/profile"
                  className="bg-nature-100 hover:bg-nature-200 text-nature-800 px-5 py-2.5 rounded-2xl text-sm font-semibold transition-all border-2 border-nature-300 flex items-center gap-2"
                >
                  <span>👤</span>
                  <span>Mon Profil</span>
                </Link>
                {user.is_producer && (
                  <Link
                    href="/producer/edit"
                    className="bg-nature-500 hover:bg-nature-600 text-white px-5 py-2.5 rounded-2xl text-sm font-semibold transition-all shadow-nature hover:shadow-nature-lg flex items-center gap-2"
                  >
                    <span>🌾</span>
                    <span>Mon Exploitation</span>
                  </Link>
                )}
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-earth-700 hover:text-nature-600 px-4 py-2 rounded-2xl text-sm font-medium transition-all hover:bg-nature-50"
                >
                  Connexion
                </Link>
                <Link
                  href="/register"
                  className="bg-nature-500 hover:bg-nature-600 text-white px-6 py-2.5 rounded-2xl text-sm font-semibold transition-all shadow-nature hover:shadow-nature-lg transform hover:scale-105"
                >
                  Inscription
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

