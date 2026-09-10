import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useMembers, useAddMember, useUpdateMember, useRemoveMember } from '@/features/members/hooks/useMembers'
import { membersApi } from '@/features/members/api/membersApi'
import type { Member } from '@/features/members/types'

vi.mock('@/features/members/api/membersApi')

const mockMember: Member = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  user_id: '223e4567-e89b-12d3-a456-426614174000',
  project_id: '323e4567-e89b-12d3-a456-426614174000',
  role: 'member',
  joined_at: new Date().toISOString(),
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

describe('useMembers hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('useMembers', () => {
    it('fetches members for project', async () => {
      const getMembersMock = vi.fn().mockResolvedValue([mockMember])
      vi.mocked(membersApi).getMembers = getMembersMock

      const { result } = renderHook(() => useMembers('project-123'), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual([mockMember])
      expect(getMembersMock).toHaveBeenCalledWith('project-123')
    })

    it('handles fetch error', async () => {
      const getMembersMock = vi.fn().mockRejectedValue(new Error('Fetch failed'))
      vi.mocked(membersApi).getMembers = getMembersMock

      const { result } = renderHook(() => useMembers('project-123'), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })

  describe('useAddMember', () => {
    it('adds member to project', async () => {
      const addMemberMock = vi.fn().mockResolvedValue(mockMember)
      vi.mocked(membersApi).addMember = addMemberMock

      const { result } = renderHook(() => useAddMember(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          data: {
            email: 'user@example.com',
          },
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockMember)
    })

    it('handles add error', async () => {
      const addMemberMock = vi.fn().mockRejectedValue(new Error('User not found'))
      vi.mocked(membersApi).addMember = addMemberMock

      const { result } = renderHook(() => useAddMember(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          data: {
            email: 'invalid@example.com',
          },
        })
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })

  describe('useUpdateMember', () => {
    it('updates member role', async () => {
      const updatedMember = { ...mockMember, role: 'admin' }
      const updateMemberMock = vi.fn().mockResolvedValue(updatedMember)
      vi.mocked(membersApi).updateMember = updateMemberMock

      const { result } = renderHook(() => useUpdateMember(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          memberId: mockMember.id,
          data: { role: 'admin' },
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(updatedMember)
    })
  })

  describe('useRemoveMember', () => {
    it('removes member from project', async () => {
      const removeMemberMock = vi.fn().mockResolvedValue(undefined)
      vi.mocked(membersApi).removeMember = removeMemberMock

      const { result } = renderHook(() => useRemoveMember(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          memberId: mockMember.id,
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })
    })

    it('handles remove error', async () => {
      const removeMemberMock = vi.fn().mockRejectedValue(new Error('Unauthorized'))
      vi.mocked(membersApi).removeMember = removeMemberMock

      const { result } = renderHook(() => useRemoveMember(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          memberId: 'member-123',
        })
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })
})
