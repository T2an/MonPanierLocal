const getBaseUrl = () => {
  const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
  return api.replace('/api', '')
}

export function getImageUrl(imagePath: string | null | undefined): string {
  if (!imagePath) return '/placeholder-image.jpg'
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) return imagePath
  const base = getBaseUrl()
  const path = imagePath.startsWith('/media/') ? imagePath : `/media/${imagePath.replace(/^\/+/, '')}`
  return `${base}${path}`
}
