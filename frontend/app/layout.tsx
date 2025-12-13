import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/hooks/useAuth'
import { Navbar } from '@/components/Navbar'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LeafletConfig } from '@/components/LeafletConfig'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Mon Panier Local - Producteurs locaux',
  description: 'Découvrez et trouvez les producteurs locaux près de chez vous',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <LeafletConfig />
        <ErrorBoundary>
          <AuthProvider>
            <Navbar />
            <main className="min-h-screen">
              {children}
            </main>
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}

