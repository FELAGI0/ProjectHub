import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useLogin, useRegister, useLogout } from '@/features/auth/hooks/useAuth'
import { useAuthStore } from '@/features/auth/store/authStore'
import { authApi } from '@/features/auth/api/authApi'
import type { User } from '@/features/auth/types'

vi.mock('@/features/auth/api/authApi')
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

const mockUser: User = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  email: 'test@example.com',
  username: 'testuser',
  is_active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

const mockAuthResponse = {
  user: mockUser,
  tokens: {
    access_token: 'access123',
    refresh_token: 'refresh456',
  },
}

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useAuth hooks integration with store', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    })
  })

  describe('useLogin updates store', () => {
    it('sets auth state in store on successful login', async () => {
      const loginMock = vi.fn().mockResolvedValue(mockAuthResponse)
      vi.mocked(authApi).login = loginMock

      const { result: hookResult } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      })

      const { result: storeResult } = renderHook(() => useAuthStore())

      expect(storeResult.current.isAuthenticated).toBe(false)

      await act(async () => {
        hookResult.current.mutate({
          email: 'test@example.com',
          password: 'password123',
        })
      })

      await waitFor(() => {
        expect(hookResult.current.isSuccess).toBe(true)
      })

      expect(storeResult.current.user).toEqual(mockUser)
      expect(storeResult.current.accessToken).toBe('access123')
      expect(storeResult.current.isAuthenticated).toBe(true)
    })
  })

  describe('useLogout clears store', () => {
    it('clears auth state from store on logout', async () => {
      const loginMock = vi.fn().mockResolvedValue(mockAuthResponse)
      const logoutMock = vi.fn().mockResolvedValue(undefined)
      vi.mocked(authApi).login = loginMock
      vi.mocked(authApi).logout = logoutMock

      const { result: loginHookResult } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      })

      const { result: logoutHookResult } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      })

      const { result: storeResult } = renderHook(() => useAuthStore())

      await act(async () => {
        loginHookResult.current.mutate({
          email: 'test@example.com',
          password: 'password123',
        })
      })

      await waitFor(() => {
        expect(storeResult.current.isAuthenticated).toBe(true)
      })

      await act(async () => {
        logoutHookResult.current.mutate()
      })

      await waitFor(() => {
        expect(logoutHookResult.current.isSuccess).toBe(true)
      })

      expect(storeResult.current.user).toBeNull()
      expect(storeResult.current.accessToken).toBeNull()
      expect(storeResult.current.isAuthenticated).toBe(false)
    })
  })
})
