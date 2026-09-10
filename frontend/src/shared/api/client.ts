import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios'
import { config } from '@/shared/config'

const apiClient: AxiosInstance = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

let refreshPromise: Promise<string> | null = null

// Request interceptor - add access token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = localStorage.getItem('access_token')

    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle 401 and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Reuse existing refresh promise if one is in flight
        if (!refreshPromise) {
          refreshPromise = (async () => {
            const refreshToken = localStorage.getItem('refresh_token')

            if (!refreshToken) {
              throw new Error('No refresh token available')
            }

            // Attempt token refresh
            const response = await axios.post<{
              tokens: {
                access_token: string
                refresh_token: string
              }
            }>(`${config.apiBaseUrl}/auth/refresh`, {
              refresh_token: refreshToken,
            })

            const { access_token, refresh_token } = response.data.tokens

            // Store new tokens
            localStorage.setItem('access_token', access_token)
            localStorage.setItem('refresh_token', refresh_token)

            return access_token
          })().finally(() => {
            refreshPromise = null
          })
        }

        const accessToken = await refreshPromise

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${accessToken}`
        }

        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        refreshPromise = null

        // Trigger auth store logout (will be implemented in auth feature)
        window.dispatchEvent(new CustomEvent('auth:logout'))

        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export { apiClient }
