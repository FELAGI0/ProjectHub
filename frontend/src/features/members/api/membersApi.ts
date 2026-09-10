import { apiClient } from '@/shared/api/client'
import type { Member, MemberAddRequest, MemberUpdateRequest } from '../types'

export const membersApi = {
  getMembers: async (projectId: string): Promise<Member[]> => {
    const response = await apiClient.get<Member[]>(
      `/projects/${projectId}/members`
    )
    return response.data
  },

  addMember: async (
    projectId: string,
    data: MemberAddRequest
  ): Promise<Member> => {
    const response = await apiClient.post<Member>(
      `/projects/${projectId}/members`,
      data
    )
    return response.data
  },

  updateMember: async (
    projectId: string,
    memberId: string,
    data: MemberUpdateRequest
  ): Promise<Member> => {
    const response = await apiClient.put<Member>(
      `/projects/${projectId}/members/${memberId}`,
      data
    )
    return response.data
  },

  removeMember: async (projectId: string, memberId: string): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/members/${memberId}`)
  },
}
