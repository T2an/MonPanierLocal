export interface User {
  id: number
  email: string
  username: string
  is_producer: boolean
  date_joined: string
}

export interface ProducerProfile {
  id: number
  user: User
  name: string
  description: string
  category: 'maraîchage' | 'élevage' | 'apiculture' | 'arboriculture' | 'céréaliculture' | 'pêche' | 'brasserie' | 'distillerie' | 'fromagerie' | 'boulangerie' | 'viticulture' | 'charcuterie' | 'autre'
  address: string
  latitude: string
  longitude: string
  phone?: string
  email_contact?: string
  website?: string
  opening_hours?: string
  photos: ProducerPhoto[]
  photo_count: number
  products?: Product[]
  created_at: string
  updated_at: string
}

export interface ProducerPhoto {
  id: number
  image_file: string
  created_at: string
}

export interface ProductCategory {
  id: number
  name: string
  icon: string
  display_name: string
  order: number
}

export interface ProductPhoto {
  id: number
  image_file: string
  created_at: string
}

export interface Product {
  id: number
  producer: ProducerProfile
  category: ProductCategory | null
  name: string
  description: string
  availability_type: 'all_year' | 'custom'
  availability_start_month: number | null
  availability_end_month: number | null
  photos: ProductPhoto[]
  photo_count: number
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  password_confirm: string
  is_producer: boolean
}

export type SaleModeType = 'on_site' | 'phone_order' | 'vending_machine' | 'delivery' | 'market'

export interface OpeningHours {
  id?: number
  day_of_week: number
  day_name?: string
  is_closed: boolean
  opening_time: string | null
  closing_time: string | null
}

export interface SaleMode {
  id?: number
  mode_type: SaleModeType
  mode_type_display?: string
  title: string
  instructions: string
  phone_number?: string
  website_url?: string
  is_24_7?: boolean
  location_address?: string
  location_latitude?: string | null
  location_longitude?: string | null
  market_info?: string
  order?: number
  opening_hours?: OpeningHours[]
  created_at?: string
  updated_at?: string
}

export interface ProducerProfile {
  id: number
  user: User
  name: string
  description: string
  category: 'maraîchage' | 'élevage' | 'apiculture' | 'arboriculture' | 'céréaliculture' | 'pêche' | 'brasserie' | 'distillerie' | 'fromagerie' | 'boulangerie' | 'viticulture' | 'charcuterie' | 'autre'
  address: string
  latitude: string
  longitude: string
  phone?: string
  email_contact?: string
  website?: string
  opening_hours?: string
  photos: ProducerPhoto[]
  photo_count: number
  products?: Product[]
  sale_modes?: SaleMode[]
  created_at: string
  updated_at: string
}

