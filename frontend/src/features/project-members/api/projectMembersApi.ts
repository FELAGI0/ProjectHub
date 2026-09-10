import { apiClient } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/api/types'
import type {
  ProjectMember,
  MemberAddRequest,
  MemberRoleUpdateRequest,
} from '../types'

export const projectMembersApi = {
  getMembers: async (
    projectId: string,
    params?: {
      page?: number
      page_size?: number
    }
  ): Promise<PaginatedResponse<ProjectMember>> => {
    const response = await apiClient.get<PaginatedResponse<ProjectMember>>(
      `/projects/${projectId}/members`,
      { params }
    )
    return response.data
  },

  addMember: async (
    projectId: string,
    data: MemberAddRequest
  ): Promise<ProjectMember> => {
    const response = await apiClient.post<ProjectMember>(
      `/projects/${projectId}/members`,
      data
    )
    return response.data
  },

  updateMemberRole: async (
    projectId: string,
    userId: string,
    data: MemberRoleUpdateRequest
  ): Promise<ProjectMember> => {
    const response = await apiClient.patch<ProjectMember>(
      `/projects/${projectId}/members/${userId}`,
      data
    )
    return response.data
  },

  removeMember: async (projectId: string, userId: string): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/members/${userId}`)
  },
}
