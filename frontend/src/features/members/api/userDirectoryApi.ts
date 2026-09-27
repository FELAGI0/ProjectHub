
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/shared/api/client'

export interface UserDirectoryItem {
  id: string
  email: string
  username: string
  is_active: boolean
  created_at: string
}

export interface UserDirectoryResponse {
  items: UserDirectoryItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface UserDirectoryParams {
  page?: number
  page_size?: number
  search?: string
}

export const userDirectoryApi = {
  list: async (params: UserDirectoryParams = {}): Promise<UserDirectoryResponse> => {
    const response = await apiClient.get<UserDirectoryResponse>('/users', {
      params,
    })
    return response.data
  },
}

export const USER_DIRECTORY_QUERY_KEY = ['users', 'directory'] as const

export function useUserDirectory(params: UserDirectoryParams = {}) {
  return useQuery({
    queryKey: [...USER_DIRECTORY_QUERY_KEY, params.page, params.page_size, params.search],
    queryFn: () => userDirectoryApi.list(params),
  })
}
