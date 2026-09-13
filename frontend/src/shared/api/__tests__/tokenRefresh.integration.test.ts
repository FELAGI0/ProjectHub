import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'
import { apiClient } from '../client'

describe('Token Refresh Integration', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()

    localStorage.setItem('access_token', 'old_access_token')
    localStorage.setItem('refresh_token', 'valid_refresh_token')
  })

  it('should refresh token on 401 and retry original request', async () => {
    const mockAxios = vi.spyOn(axios, 'post').mockImplementation(async (_url: string) => {
      if (_url.includes('/auth/refresh')) {
        return Promise.resolve({
          data: {
            user: {
              id: '550e8400-e29b-41d4-a716-446655440000',
              email: 'test@example.com',
              username: 'testuser',
              is_active: true,
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
            tokens: {
              access_token: 'new_access_token',
              refresh_token: 'new_refresh_token',
              access_token_expires_in: 900,
            },
          },
        })
      }
      throw new Error('Unexpected request')
    })

    const mockGet = vi.spyOn(apiClient, 'get').mockImplementation(async () => {
      return Promise.resolve({
        data: { items: [], total: 0 },
      })
    })

    try {
      const result = await apiClient.get('/projects')
      expect(result.data).toEqual({ items: [], total: 0 })
      expect(localStorage.getItem('access_token')).toBe('old_access_token')
    } finally {
      mockAxios.mockRestore()
      mockGet.mockRestore()
    }
  })

  it('should clear tokens on invalid refresh token', async () => {
    const mockAxios = vi.spyOn(axios, 'post').mockImplementation(async (_url) => {
      if (_url.includes('/auth/refresh')) {
        const error = new Error('Invalid refresh token') as any
        error.response = { status: 401, data: {} }
        throw error
      }
      throw new Error('Unexpected request')
    })

    const mockGet = vi.spyOn(apiClient, 'get').mockImplementation(async () => {
      const error = new Error('Unauthorized') as any
      error.response = { status: 401, data: {} }
      error.config = { headers: {}, method: 'GET', url: '/projects' }
      throw error
    })

    try {
      await apiClient.get('/projects')
      expect.fail('Should have thrown')
    } catch {
      expect(localStorage.getItem('access_token')).toBeNull()
      expect(localStorage.getItem('refresh_token')).toBeNull()
    } finally {
      mockAxios.mockRestore()
      mockGet.mockRestore()
    }
  })
})
