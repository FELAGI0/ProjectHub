import { apiClient } from '@/shared/api/client'
import type { AuthResponse, LoginRequest, RegisterRequest } from '../types'

export const authApi = {
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', data)
    return response.data
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', data)
    return response.data
  },

  refresh: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  logout: async (): Promise<void> => {
    return Promise.resolve()
  },

  getProfile: async () => {
    const response = await apiClient.get('/users/me')
    return response.data
  },

  updateProfile: async (data: { username?: string; email?: string }) => {
    const response = await apiClient.patch('/users/me', data)
    return response.data
  },
}
