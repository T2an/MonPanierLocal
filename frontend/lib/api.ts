import axios, { AxiosInstance } from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL?.startsWith('http')
  ? process.env.NEXT_PUBLIC_API_URL
  : process.env.NEXT_PUBLIC_API_URL === '/api'
  ? '/api'
  : 'http://localhost:8000/api'

const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

axiosInstance.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = Cookies.get('refresh_token')
        if (refreshToken) {
          const res = await axios.post(`${API_URL}/auth/token/refresh/`, { refresh: refreshToken })
          Cookies.set('access_token', res.data.access)
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`
          return axiosInstance(originalRequest)
        }
      } catch {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        if (typeof window !== 'undefined') window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const apiClient = {
  login: (creds: { email: string; password: string }) =>
    axiosInstance.post('/auth/login/', creds).then((r) => {
      Cookies.set('access_token', r.data.access, { expires: 1 })
      Cookies.set('refresh_token', r.data.refresh, { expires: 7 })
      return r.data
    }),
  register: (data: unknown) => axiosInstance.post('/auth/register/', data).then((r) => r.data),
  logout: () => {
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
  },
  getMe: () => axiosInstance.get('/auth/me/').then((r) => r.data),
  updateMe: (data: unknown) => axiosInstance.patch('/auth/me/', data).then((r) => r.data),
  changePassword: (data: { old_password: string; new_password: string }) =>
    axiosInstance.post('/auth/change-password/', data).then((r) => r.data),

  getProducers: (params?: { search?: string; categories?: string[] }) => {
    const q: Record<string, string> = {}
    if (params?.search) q.search = params.search
    if (params?.categories?.length) q.categories = params.categories.join(',')
    return axiosInstance.get('/producers/', { params: q }).then((r) => r.data)
  },
  getProducer: (id: number) => axiosInstance.get(`/producers/${id}/`).then((r) => r.data),
  getNearbyProducers: (params: {
    latitude: number
    longitude: number
    radius_km?: number
    categories?: string[]
  }) => {
    const q: Record<string, string | number> = {
      latitude: params.latitude,
      longitude: params.longitude,
      ...(params.radius_km != null && { radius_km: params.radius_km }),
    }
    if (params.categories?.length) q.categories = params.categories.join(',')
    return axiosInstance.get('/producers/nearby/', { params: q }).then((r) => r.data)
  },
  createProducer: (data: FormData | Record<string, unknown>) =>
    data instanceof FormData
      ? axiosInstance.post('/producers/', data, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data)
      : axiosInstance.post('/producers/', data).then((r) => r.data),
  updateProducer: (id: number, data: FormData | Record<string, unknown>) =>
    axiosInstance.patch(`/producers/${id}/`, data).then((r) => r.data),

  uploadPhoto: (producerId: number, file: File) => {
    const fd = new FormData()
    fd.append('photo', file)
    return axiosInstance.post(`/producers/${producerId}/photos/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },
  deletePhoto: (photoId: number) => axiosInstance.delete(`/photos/${photoId}/`).then((r) => r.data),

  getSaleModes: (producerId: number) =>
    axiosInstance.get(`/producers/${producerId}/sale-modes/`).then((r) => r.data.results ?? r.data),
  createSaleMode: (producerId: number, data: unknown) =>
    axiosInstance.post(`/producers/${producerId}/sale-modes/`, data).then((r) => r.data),
  updateSaleMode: (producerId: number, modeId: number, data: unknown) =>
    axiosInstance.patch(`/producers/${producerId}/sale-modes/${modeId}/`, data).then((r) => r.data),
  deleteSaleMode: (producerId: number, modeId: number) =>
    axiosInstance.delete(`/producers/${producerId}/sale-modes/${modeId}/`).then((r) => r.data),

  getProductCategories: () => axiosInstance.get('/products/categories/').then((r) => r.data),
  createProduct: (producerId: number, data: unknown) =>
    axiosInstance.post(`/producers/${producerId}/products/`, data).then((r) => r.data),
  updateProduct: (productId: number, data: unknown) =>
    axiosInstance.patch(`/products/${productId}/`, data).then((r) => r.data),
  deleteProduct: (productId: number) => axiosInstance.delete(`/products/${productId}/`).then((r) => r.data),
  uploadProductPhoto: (productId: number, file: File) => {
    const fd = new FormData()
    fd.append('photo', file)
    return axiosInstance.post(`/products/${productId}/photos/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },
  deleteProductPhoto: (photoId: number) =>
    axiosInstance.delete(`/products/photos/${photoId}/`).then((r) => r.data),
}
