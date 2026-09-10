import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { membersApi } from '../api/membersApi'
import type { MemberAddRequest, MemberUpdateRequest } from '../types'

const MEMBERS_QUERY_KEY = ['members'] as const

export const useMembers = (projectId: string) => {
  return useQuery({
    queryKey: [...MEMBERS_QUERY_KEY, projectId],
    queryFn: () => membersApi.getMembers(projectId),
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
    }) => membersApi.addMember(projectId, data),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [...MEMBERS_QUERY_KEY, variables.projectId],
      })
    },
  })
}

export const useUpdateMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      projectId,
      memberId,
      data,
    }: {
      projectId: string
      memberId: string
      data: MemberUpdateRequest
    }) => membersApi.updateMember(projectId, memberId, data),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [...MEMBERS_QUERY_KEY, variables.projectId],
      })
    },
  })
}

export const useRemoveMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      projectId,
      memberId,
    }: {
      projectId: string
      memberId: string
    }) => membersApi.removeMember(projectId, memberId),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [...MEMBERS_QUERY_KEY, variables.projectId],
      })
    },
  })
}
