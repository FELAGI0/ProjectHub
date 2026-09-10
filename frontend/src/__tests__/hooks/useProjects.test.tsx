import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useProjects, useProject, useCreateProject, useUpdateProject, useDeleteProject } from '@/features/projects/hooks/useProjects'
import { projectsApi } from '@/features/projects/api/projectsApi'
import type { Project } from '@/features/projects/types'

vi.mock('@/features/projects/api/projectsApi')

const mockProject: Project = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  name: 'Test Project',
  description: 'A test project',
  owner_id: '123e4567-e89b-12d3-a456-426614174001',
  is_active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

const mockPaginatedResponse = {
  items: [mockProject],
  total: 1,
  page: 1,
  page_size: 20,
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

describe('useProjects hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('useProjects', () => {
    it('fetches projects list', async () => {
      const getProjectsMock = vi.fn().mockResolvedValue(mockPaginatedResponse)
      vi.mocked(projectsApi).getProjects = getProjectsMock

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockPaginatedResponse)
    })

    it('handles fetch error', async () => {
      const getProjectsMock = vi.fn().mockRejectedValue(new Error('Fetch failed'))
      vi.mocked(projectsApi).getProjects = getProjectsMock

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })

    it('passes pagination parameters', async () => {
      const getProjectsMock = vi.fn().mockResolvedValue(mockPaginatedResponse)
      vi.mocked(projectsApi).getProjects = getProjectsMock

      renderHook(() => useProjects({ page: 2, page_size: 10, search: 'api' }), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(getProjectsMock).toHaveBeenCalledWith({
          page: 2,
          page_size: 10,
          search: 'api',
        })
      })
    })
  })

  describe('useProject', () => {
    it('fetches single project', async () => {
      const getProjectMock = vi.fn().mockResolvedValue(mockProject)
      vi.mocked(projectsApi).getProject = getProjectMock

      const { result } = renderHook(() => useProject(mockProject.id), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockProject)
    })

    it('handles fetch error for single project', async () => {
      const getProjectMock = vi.fn().mockRejectedValue(new Error('Not found'))
      vi.mocked(projectsApi).getProject = getProjectMock

      const { result } = renderHook(() => useProject('invalid-id'), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })

  describe('useCreateProject', () => {
    it('creates new project', async () => {
      const createProjectMock = vi.fn().mockResolvedValue(mockProject)
      vi.mocked(projectsApi).createProject = createProjectMock

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          name: 'Test Project',
          description: 'A test project',
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockProject)
    })

    it('handles creation error', async () => {
      const createProjectMock = vi.fn().mockRejectedValue(new Error('Validation failed'))
      vi.mocked(projectsApi).createProject = createProjectMock

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          name: '',
          description: 'A test project',
        })
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })

  describe('useUpdateProject', () => {
    it('updates project', async () => {
      const updatedProject = { ...mockProject, name: 'Updated Project' }
      const updateProjectMock = vi.fn().mockResolvedValue(updatedProject)
      vi.mocked(projectsApi).updateProject = updateProjectMock

      const { result } = renderHook(() => useUpdateProject(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          id: mockProject.id,
          data: { name: 'Updated Project' },
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(updatedProject)
    })
  })

  describe('useDeleteProject', () => {
    it('deletes project', async () => {
      const deleteProjectMock = vi.fn().mockResolvedValue(undefined)
      vi.mocked(projectsApi).deleteProject = deleteProjectMock

      const { result } = renderHook(() => useDeleteProject(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate(mockProject.id)
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })
    })

    it('handles deletion error', async () => {
      const deleteProjectMock = vi.fn().mockRejectedValue(new Error('Unauthorized'))
      vi.mocked(projectsApi).deleteProject = deleteProjectMock

      const { result } = renderHook(() => useDeleteProject(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate('invalid-id')
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })
})
