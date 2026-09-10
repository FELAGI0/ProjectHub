import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useLogin, useRegister, useLogout } from '@/features/auth/hooks/useAuth'
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

describe('useAuth hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('useLogin', () => {
    it('successfully logs in user', async () => {
      const loginMock = vi.fn().mockResolvedValue(mockAuthResponse)
      vi.mocked(authApi).login = loginMock

      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          email: 'test@example.com',
          password: 'password123',
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockAuthResponse)
    })

    it('handles login error', async () => {
      const loginMock = vi.fn().mockRejectedValue(new Error('Login failed'))
      vi.mocked(authApi).login = loginMock

      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          email: 'test@example.com',
          password: 'wrong',
        })
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })

  describe('useRegister', () => {
    it('successfully registers user', async () => {
      const registerMock = vi.fn().mockResolvedValue(mockAuthResponse)
      vi.mocked(authApi).register = registerMock

      const { result } = renderHook(() => useRegister(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          email: 'newuser@example.com',
          username: 'newuser',
          password: 'password123',
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockAuthResponse)
    })

    it('handles registration error', async () => {
      const registerMock = vi.fn().mockRejectedValue(
        new Error('Email already exists')
      )
      vi.mocked(authApi).register = registerMock

      const { result } = renderHook(() => useRegister(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          email: 'existing@example.com',
          username: 'existing',
          password: 'password123',
        })
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })

  describe('useLogout', () => {
    it('successfully logs out user', async () => {
      const logoutMock = vi.fn().mockResolvedValue(undefined)
      vi.mocked(authApi).logout = logoutMock

      const { result } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate()
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })
    })

    it('handles logout error', async () => {
      const logoutMock = vi.fn().mockRejectedValue(new Error('Logout failed'))
      vi.mocked(authApi).logout = logoutMock

      const { result } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate()
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })
})
