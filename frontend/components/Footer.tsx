'use client'

import Link from 'next/link'

export function Footer() {
  return (
    <footer className="bg-earth-800 text-white border-t-4 border-nature-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Logo et description */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-3xl">🌾</span>
              <span className="text-xl font-bold text-nature-300">Mon Panier Local</span>
            </div>
            <p className="text-earth-300 text-sm">
              Trouvez les producteurs locaux près de chez vous et achetez directement à la ferme.
            </p>
          </div>

          {/* Liens utiles */}
          <div>
            <h3 className="text-sm font-semibold text-nature-300 uppercase tracking-wide mb-4">
              Liens utiles
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/about"
                  className="text-earth-300 hover:text-white transition-colors text-sm"
                >
                  À propos
                </Link>
              </li>
              <li>
                <Link
                  href="/register"
                  className="text-earth-300 hover:text-white transition-colors text-sm"
                >
                  Devenir producteur
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-sm font-semibold text-nature-300 uppercase tracking-wide mb-4">
              Contact
            </h3>
            <p className="text-earth-300 text-sm mb-3">
              Une question ? Une suggestion ?
            </p>
            <Link
              href="/contact"
              className="inline-flex items-center gap-2 px-4 py-2 bg-nature-600 hover:bg-nature-500 text-white rounded-xl text-sm font-medium transition-all"
            >
              <span>✉️</span>
              <span>Nous contacter</span>
            </Link>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-6 border-t border-earth-700">
          <p className="text-center text-earth-400 text-sm">
            © {new Date().getFullYear()} Mon Panier Local. Tous droits réservés.
          </p>
        </div>
      </div>
    </footer>
  )
}


