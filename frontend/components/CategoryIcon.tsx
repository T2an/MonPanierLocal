'use client'

import type { ProductCategory } from '@/types'

interface CategoryIconProps {
  category: ProductCategory | null
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const iconMap: Record<string, string> = {
  carrot: '🥕',
  apple: '🍎',
  wheat: '🌾',
  bread: '🍞',
  honey: '🍯',
  meat: '🥩',
  beer: '🍺',
  package: '📦',
}

const sizeClasses = {
  sm: 'text-lg',
  md: 'text-2xl',
  lg: 'text-4xl',
}

export function CategoryIcon({ category, size = 'md', className = '' }: CategoryIconProps) {
  if (!category) {
    return <span className={`${sizeClasses[size]} ${className}`}>📦</span>
  }

  const emoji = iconMap[category.icon] || '📦'
  return <span className={`${sizeClasses[size]} ${className}`}>{emoji}</span>
}


