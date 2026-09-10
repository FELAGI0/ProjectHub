import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAuthStore } from '@/features/auth/store/authStore'
import type { User } from '@/features/auth/types'

const mockUser: User = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  email: 'test@example.com',
  username: 'testuser',
  is_active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    })
    localStorage.clear()
  })

  it('initializes with null state', () => {
    const { result } = renderHook(() => useAuthStore())

    expect(result.current.user).toBeNull()
    expect(result.current.accessToken).toBeNull()
    expect(result.current.refreshToken).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('sets auth state and stores tokens in localStorage', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setAuth(mockUser, 'access123', 'refresh456')
    })

    expect(result.current.user).toEqual(mockUser)
    expect(result.current.accessToken).toBe('access123')
    expect(result.current.refreshToken).toBe('refresh456')
    expect(result.current.isAuthenticated).toBe(true)
    expect(localStorage.getItem('access_token')).toBe('access123')
    expect(localStorage.getItem('refresh_token')).toBe('refresh456')
  })

  it('clears auth state and removes tokens from localStorage', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setAuth(mockUser, 'access123', 'refresh456')
    })

    expect(result.current.isAuthenticated).toBe(true)

    act(() => {
      result.current.clearAuth()
    })

    expect(result.current.user).toBeNull()
    expect(result.current.accessToken).toBeNull()
    expect(result.current.refreshToken).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('updates tokens without changing user', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setAuth(mockUser, 'access123', 'refresh456')
    })

    const newAccessToken = 'newaccess789'
    const newRefreshToken = 'newrefresh012'

    act(() => {
      result.current.setAuth(mockUser, newAccessToken, newRefreshToken)
    })

    expect(result.current.user).toEqual(mockUser)
    expect(result.current.accessToken).toBe(newAccessToken)
    expect(result.current.refreshToken).toBe(newRefreshToken)
  })
})
