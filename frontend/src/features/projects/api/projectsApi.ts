import { apiClient } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/api/types'
import type {
  Project,
  ProjectCreateRequest,
  ProjectUpdateRequest,
} from '../types'

export const projectsApi = {
  getProjects: async (params?: {
    page?: number
    page_size?: number
    search?: string
    is_active?: boolean
  }): Promise<PaginatedResponse<Project>> => {
    const response = await apiClient.get<PaginatedResponse<Project>>(
      '/projects',
      { params }
    )
    return response.data
  },

  getProject: async (id: string): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${id}`)
    return response.data
  },

  createProject: async (data: ProjectCreateRequest): Promise<Project> => {
    const response = await apiClient.post<Project>('/projects', data)
    return response.data
  },

  updateProject: async (
    id: string,
    data: ProjectUpdateRequest
  ): Promise<Project> => {
    const response = await apiClient.patch<Project>(`/projects/${id}`, data)
    return response.data
  },

  deleteProject: async (id: string): Promise<void> => {
    await apiClient.delete(`/projects/${id}`)
  },
}
