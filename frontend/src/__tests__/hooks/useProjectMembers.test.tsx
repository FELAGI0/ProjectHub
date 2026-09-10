import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useProjectMembers, useAddMember, useUpdateMemberRole, useRemoveMember } from '@/features/project-members/hooks/useProjectMembers'
import { projectMembersApi } from '@/features/project-members/api/projectMembersApi'
import type { ProjectMember } from '@/features/project-members/types'

vi.mock('@/features/project-members/api/projectMembersApi')
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

const mockMember: ProjectMember = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  project_id: '223e4567-e89b-12d3-a456-426614174000',
  user_id: '323e4567-e89b-12d3-a456-426614174000',
  role: 'member',
  joined_at: new Date().toISOString(),
}

const mockMembersResponse = {
  items: [mockMember],
  total: 1,
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

describe('useProjectMembers hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('useProjectMembers', () => {
    it('fetches members for project', async () => {
      const getMembersMock = vi.fn().mockResolvedValue(mockMembersResponse)
      vi.mocked(projectMembersApi).getMembers = getMembersMock

      const { result } = renderHook(() => useProjectMembers('project-123'), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockMembersResponse)
      expect(getMembersMock).toHaveBeenCalledWith('project-123', undefined)
    })

    it('passes pagination parameters', async () => {
      const getMembersMock = vi.fn().mockResolvedValue(mockMembersResponse)
      vi.mocked(projectMembersApi).getMembers = getMembersMock

      renderHook(() => useProjectMembers('project-123', { page: 2, page_size: 10 }), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(getMembersMock).toHaveBeenCalledWith('project-123', {
          page: 2,
          page_size: 10,
        })
      })
    })
  })

  describe('useAddMember', () => {
    it('adds member to project', async () => {
      const addMemberMock = vi.fn().mockResolvedValue(mockMember)
      vi.mocked(projectMembersApi).addMember = addMemberMock

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
      vi.mocked(projectMembersApi).addMember = addMemberMock

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

  describe('useUpdateMemberRole', () => {
    it('updates member role', async () => {
      const updatedMember = { ...mockMember, role: 'admin' }
      const updateRoleMock = vi.fn().mockResolvedValue(updatedMember)
      vi.mocked(projectMembersApi).updateMemberRole = updateRoleMock

      const { result } = renderHook(() => useUpdateMemberRole(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          userId: mockMember.user_id,
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
      vi.mocked(projectMembersApi).removeMember = removeMemberMock

      const { result } = renderHook(() => useRemoveMember(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          userId: mockMember.user_id,
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })
    })

    it('handles remove error', async () => {
      const removeMemberMock = vi.fn().mockRejectedValue(new Error('Unauthorized'))
      vi.mocked(projectMembersApi).removeMember = removeMemberMock

      const { result } = renderHook(() => useRemoveMember(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          userId: 'user-123',
        })
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })
})
