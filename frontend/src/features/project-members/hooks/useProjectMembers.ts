import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { projectMembersApi } from '../api/projectMembersApi'
import type { MemberAddRequest, MemberRoleUpdateRequest } from '../types'
import { SUCCESS_MESSAGES, ERROR_MESSAGES } from '@/shared/constants/messages'

const MEMBERS_QUERY_KEY = ['project-members'] as const

export const useProjectMembers = (
  projectId: string,
  params?: {
    page?: number
    page_size?: number
  }
) => {
  return useQuery({
    queryKey: [...MEMBERS_QUERY_KEY, projectId, params],
    queryFn: () => projectMembersApi.getMembers(projectId, params),
    enabled: !!projectId,
  })
}

export const useAddMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string
      data: MemberAddRequest
    }) => projectMembersApi.addMember(projectId, data),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [...MEMBERS_QUERY_KEY, variables.projectId],
      })
      toast.success(SUCCESS_MESSAGES.member.added)
    },
    onError: () => {
      toast.error(ERROR_MESSAGES.member.add)
    },
  })
}

export const useUpdateMemberRole = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      projectId,
      userId,
      data,
    }: {
      projectId: string
      userId: string
      data: MemberRoleUpdateRequest
    }) => projectMembersApi.updateMemberRole(projectId, userId, data),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [...MEMBERS_QUERY_KEY, variables.projectId],
      })
      toast.success(SUCCESS_MESSAGES.member.roleUpdated)
    },
    onError: () => {
      toast.error(ERROR_MESSAGES.member.updateRole)
    },
  })
}

export const useRemoveMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ projectId, userId }: { projectId: string; userId: string }) =>
      projectMembersApi.removeMember(projectId, userId),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [...MEMBERS_QUERY_KEY, variables.projectId],
      })
      toast.success(SUCCESS_MESSAGES.member.removed)
    },
    onError: () => {
      toast.error(ERROR_MESSAGES.member.remove)
    },
  })
}
