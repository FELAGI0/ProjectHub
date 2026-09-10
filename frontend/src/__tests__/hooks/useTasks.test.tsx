import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useTasks, useTask, useCreateTask, useUpdateTask, useDeleteTask } from '@/features/tasks/hooks/useTasks'
import { tasksApi } from '@/features/tasks/api/tasksApi'
import type { Task } from '@/features/tasks/types'

vi.mock('@/features/tasks/api/tasksApi')
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

const mockTask: Task = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  project_id: '223e4567-e89b-12d3-a456-426614174000',
  title: 'Test Task',
  description: 'A test task',
  status: 'todo',
  priority: 'medium',
  assigned_to: null,
  due_date: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

const mockTasksResponse = {
  items: [mockTask],
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

describe('useTasks hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('useTasks', () => {
    it('fetches tasks for project', async () => {
      const getTasksMock = vi.fn().mockResolvedValue(mockTasksResponse)
      vi.mocked(tasksApi).getTasks = getTasksMock

      const { result } = renderHook(() => useTasks('project-123'), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockTasksResponse)
      expect(getTasksMock).toHaveBeenCalledWith('project-123', undefined)
    })

    it('passes filter parameters', async () => {
      const getTasksMock = vi.fn().mockResolvedValue(mockTasksResponse)
      vi.mocked(tasksApi).getTasks = getTasksMock

      renderHook(() => useTasks('project-123', { status: 'in_progress', priority: 'high' }), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(getTasksMock).toHaveBeenCalledWith('project-123', {
          status: 'in_progress',
          priority: 'high',
        })
      })
    })
  })

  describe('useTask', () => {
    it('fetches single task', async () => {
      const getTaskMock = vi.fn().mockResolvedValue(mockTask)
      vi.mocked(tasksApi).getTask = getTaskMock

      const { result } = renderHook(() => useTask(mockTask.id), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockTask)
    })

    it('handles fetch error', async () => {
      const getTaskMock = vi.fn().mockRejectedValue(new Error('Not found'))
      vi.mocked(tasksApi).getTask = getTaskMock

      const { result } = renderHook(() => useTask('invalid-id'), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })

  describe('useCreateTask', () => {
    it('creates new task', async () => {
      const createTaskMock = vi.fn().mockResolvedValue(mockTask)
      vi.mocked(tasksApi).createTask = createTaskMock

      const { result } = renderHook(() => useCreateTask(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          data: {
            title: 'Test Task',
            description: 'A test task',
            status: 'todo',
            priority: 'medium',
          },
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockTask)
    })

    it('handles creation error', async () => {
      const createTaskMock = vi.fn().mockRejectedValue(new Error('Validation failed'))
      vi.mocked(tasksApi).createTask = createTaskMock

      const { result } = renderHook(() => useCreateTask(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          projectId: 'project-123',
          data: {
            title: '',
            status: 'todo',
            priority: 'medium',
          },
        })
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })

  describe('useUpdateTask', () => {
    it('updates task', async () => {
      const updatedTask = { ...mockTask, status: 'in_progress' }
      const updateTaskMock = vi.fn().mockResolvedValue(updatedTask)
      vi.mocked(tasksApi).updateTask = updateTaskMock

      const { result } = renderHook(() => useUpdateTask(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          taskId: mockTask.id,
          data: { status: 'in_progress' },
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(updatedTask)
    })
  })

  describe('useDeleteTask', () => {
    it('deletes task', async () => {
      const deleteTaskMock = vi.fn().mockResolvedValue(undefined)
      vi.mocked(tasksApi).deleteTask = deleteTaskMock

      const { result } = renderHook(() => useDeleteTask(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          taskId: mockTask.id,
          projectId: mockTask.project_id,
        })
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })
    })

    it('handles deletion error', async () => {
      const deleteTaskMock = vi.fn().mockRejectedValue(new Error('Unauthorized'))
      vi.mocked(tasksApi).deleteTask = deleteTaskMock

      const { result } = renderHook(() => useDeleteTask(), {
        wrapper: createWrapper(),
      })

      await act(async () => {
        result.current.mutate({
          taskId: 'invalid-id',
          projectId: 'project-123',
        })
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })
    })
  })
})
