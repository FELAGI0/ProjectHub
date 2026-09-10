import { apiClient } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/api/types'
import type { Task, TaskCreateRequest, TaskUpdateRequest } from '../types'

export const tasksApi = {
  getTasks: async (
    projectId: string,
    params?: {
      page?: number
      page_size?: number
      status?: string
      priority?: string
      search?: string
    }
  ): Promise<PaginatedResponse<Task>> => {
    const response = await apiClient.get<PaginatedResponse<Task>>(
      `/projects/${projectId}/tasks`,
      { params }
    )
    return response.data
  },

  getTask: async (taskId: string): Promise<Task> => {
    const response = await apiClient.get<Task>(`/tasks/${taskId}`)
    return response.data
  },

  createTask: async (
    projectId: string,
    data: TaskCreateRequest
  ): Promise<Task> => {
    const response = await apiClient.post<Task>(
      `/projects/${projectId}/tasks`,
      data
    )
    return response.data
  },

  updateTask: async (
    taskId: string,
    data: TaskUpdateRequest
  ): Promise<Task> => {
    const response = await apiClient.put<Task>(`/tasks/${taskId}`, data)
    return response.data
  },

  deleteTask: async (taskId: string): Promise<void> => {
    await apiClient.delete(`/tasks/${taskId}`)
  },
}
