import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { apiClient } from '@/shared/api/client'
import { tasksApi } from '../api/tasksApi'
import type { Task, TaskCreateRequest, TaskUpdateRequest } from '../types'
import { SUCCESS_MESSAGES, ERROR_MESSAGES } from '@/shared/constants/messages'

interface TasksResponse {
  items: Task[]
  total: number
}

const TASKS_QUERY_KEY = ['tasks'] as const

export const useTasks = (
  projectId: string,
  params?: {
    page?: number
    page_size?: number
    status?: string
    priority?: string
    search?: string
  }
) => {
  return useQuery({
    queryKey: [...TASKS_QUERY_KEY, projectId, params],
    queryFn: () => tasksApi.getTasks(projectId, params),
    enabled: !!projectId,
  })
}

export const useTask = (taskId: string) => {
  return useQuery({
    queryKey: [...TASKS_QUERY_KEY, taskId],
    queryFn: () => tasksApi.getTask(taskId),
    enabled: !!taskId,
  })
}

export const useCreateTask = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string
      data: TaskCreateRequest
    }) => tasksApi.createTask(projectId, data),
    onMutate: async ({ projectId, data }) => {
      await queryClient.cancelQueries({
        queryKey: [...TASKS_QUERY_KEY, projectId],
      })

      const previousTasks = queryClient.getQueryData([...TASKS_QUERY_KEY, projectId])

      queryClient.setQueryData([...TASKS_QUERY_KEY, projectId], (old: TasksResponse | undefined) => {
        if (!old) return old
        return {
          ...old,
          items: [
            {
              ...data,
              id: 'temp-' + Date.now(),
              project_id: projectId,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
            ...old.items,
          ],
          total: old.total + 1,
        }
      })

      return { previousTasks, projectId }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData([...TASKS_QUERY_KEY, context.projectId], context.previousTasks)
      }
      toast.error(ERROR_MESSAGES.task.create)
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [...TASKS_QUERY_KEY, variables.projectId],
      })
      toast.success(SUCCESS_MESSAGES.task.created)
    },
  })
}

export const useUpdateTask = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      taskId,
      data,
    }: {
      taskId: string
      data: TaskUpdateRequest
    }) => tasksApi.updateTask(taskId, data),
    onMutate: async ({ taskId, data }) => {
      await queryClient.cancelQueries({ queryKey: [...TASKS_QUERY_KEY, taskId] })

      const previousTask = queryClient.getQueryData([...TASKS_QUERY_KEY, taskId])

      queryClient.setQueryData([...TASKS_QUERY_KEY, taskId], (old: Task | undefined) => ({
        ...old,
        ...data,
      } as Task))

      return { previousTask, taskId }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousTask) {
        queryClient.setQueryData([...TASKS_QUERY_KEY, context.taskId], context.previousTask)
      }
      toast.error(ERROR_MESSAGES.task.update)
    },
    onSuccess: (updatedTask: Task) => {
      void queryClient.invalidateQueries({
        queryKey: [...TASKS_QUERY_KEY, updatedTask.project_id],
      })
      void queryClient.invalidateQueries({
        queryKey: [...TASKS_QUERY_KEY, updatedTask.id],
      })
      toast.success(SUCCESS_MESSAGES.task.updated)
    },
  })
}

export const useDeleteTask = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      taskId,
      projectId,
    }: {
      taskId: string
      projectId: string
    }) => {
      void projectId
      return tasksApi.deleteTask(taskId)
    },
    onMutate: async ({ taskId, projectId }) => {
      await queryClient.cancelQueries({
        queryKey: [...TASKS_QUERY_KEY, projectId],
      })

      const previousTasks = queryClient.getQueryData([...TASKS_QUERY_KEY, projectId])

      queryClient.setQueryData([...TASKS_QUERY_KEY, projectId], (old: TasksResponse | undefined) => {
        if (!old) return old
        return {
          ...old,
          items: old.items.filter((t: Task) => t.id !== taskId),
          total: old.total - 1,
        }
      })

      return { previousTasks, projectId }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData([...TASKS_QUERY_KEY, context.projectId], context.previousTasks)
      }
      toast.error(ERROR_MESSAGES.task.delete)
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [...TASKS_QUERY_KEY, variables.projectId],
      })
      toast.success(SUCCESS_MESSAGES.task.deleted)
    },
  })
}

export const useTotalTasksCount = () => {
  const { data: projectsData } = useQuery({
    queryKey: ['projects', 'all'],
    queryFn: async () => {
      const response = await apiClient.get<{ items: any[]; total: number }>(
        '/projects',
        { params: { page_size: 1000 } }
      )
      return response.data
    },
  })

  const tasksQuery = useQuery({
    queryKey: ['tasks', 'total-count'],
    queryFn: async () => {
      if (!projectsData?.items?.length) return 0

      let total = 0
      for (const project of projectsData.items) {
        try {
          const response = await tasksApi.getTasks(project.id, { page_size: 1 })
          total += response.total
        } catch {
          // ignore project access errors
        }
      }
      return total
    },
    enabled: !!projectsData?.items?.length,
  })

  return tasksQuery
}
