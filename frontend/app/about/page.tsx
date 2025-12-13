import Link from 'next/link'

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link
        href="/"
        className="text-primary-600 hover:text-primary-700 mb-4 inline-block"
      >
        ← Retour à l'accueil
      </Link>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-4xl font-bold mb-6">À propos de Mon Panier Local</h1>

        <div className="prose max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Notre Mission</h2>
            <p className="text-gray-700 mb-4">
              Mon Panier Local est une plateforme dédiée à la promotion des producteurs locaux.
              Notre objectif est de faciliter la découverte et le contact avec les producteurs
              près de chez vous, favorisant ainsi les circuits courts et une consommation plus
              responsable.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Comment ça marche ?</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-semibold mb-2">Pour les consommateurs</h3>
                <p className="text-gray-700">
                  Explorez la carte interactive pour découvrir les producteurs locaux autour de vous.
                  Filtrez par catégorie, recherchez par nom ou produit, et contactez directement
                  les producteurs qui vous intéressent.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Pour les producteurs</h3>
                <p className="text-gray-700">
                  Créez votre profil gratuitement, ajoutez vos produits, vos photos et vos informations
                  de contact. Augmentez votre visibilité et connectez-vous avec vos clients locaux.
                </p>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Nos Valeurs</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Promouvoir les circuits courts et l'agriculture locale</li>
              <li>Faciliter le contact direct entre producteurs et consommateurs</li>
              <li>Encourager une consommation responsable et durable</li>
              <li>Valoriser le travail des producteurs locaux</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Contact</h2>
            <p className="text-gray-700">
              Pour toute question ou suggestion, n'hésitez pas à nous contacter via la{' '}
              <Link href="/contact" className="text-primary-600 hover:text-primary-700">
                page de contact
              </Link>
              .
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

