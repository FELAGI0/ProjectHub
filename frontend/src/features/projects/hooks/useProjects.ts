import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { projectsApi } from '../api/projectsApi'
import type { Project, ProjectCreateRequest, ProjectUpdateRequest } from '../types'
import { SUCCESS_MESSAGES, ERROR_MESSAGES } from '@/shared/constants/messages'

interface ProjectsResponse {
  items: Project[]
  total: number
}

const PROJECTS_QUERY_KEY = ['projects'] as const

export const useProjects = (params?: {
  page?: number
  page_size?: number
  search?: string
  is_active?: boolean
}) => {
  return useQuery({
    queryKey: [...PROJECTS_QUERY_KEY, params],
    queryFn: () => projectsApi.getProjects(params),
  })
}

export const useProject = (id: string) => {
  return useQuery({
    queryKey: [...PROJECTS_QUERY_KEY, id],
    queryFn: () => projectsApi.getProject(id),
    enabled: !!id,
  })
}

export const useCreateProject = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ProjectCreateRequest) =>
      projectsApi.createProject(data),
    onMutate: async (newProject) => {
      await queryClient.cancelQueries({ queryKey: PROJECTS_QUERY_KEY })

      const previousProjects = queryClient.getQueryData(PROJECTS_QUERY_KEY)

      queryClient.setQueryData(PROJECTS_QUERY_KEY, (old: ProjectsResponse | undefined) => {
        if (!old) return old
        return {
          ...old,
          items: [{ ...newProject, id: 'temp-' + Date.now(), created_at: new Date().toISOString(), updated_at: new Date().toISOString(), is_active: true }, ...old.items],
          total: old.total + 1,
        }
      })

      return { previousProjects }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(PROJECTS_QUERY_KEY, context.previousProjects)
      }
      toast.error(ERROR_MESSAGES.project.create)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY })
      toast.success(SUCCESS_MESSAGES.project.created)
    },
  })
}

export const useUpdateProject = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProjectUpdateRequest }) =>
      projectsApi.updateProject(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: [...PROJECTS_QUERY_KEY, id] })

      const previousProject = queryClient.getQueryData([...PROJECTS_QUERY_KEY, id])

      queryClient.setQueryData([...PROJECTS_QUERY_KEY, id], (old: Project | undefined) => ({
        ...old,
        ...data,
      } as Project))

      return { previousProject, id }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousProject) {
        queryClient.setQueryData([...PROJECTS_QUERY_KEY, context.id], context.previousProject)
      }
      toast.error(ERROR_MESSAGES.project.update)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY })
      toast.success(SUCCESS_MESSAGES.project.updated)
    },
  })
}

export const useDeleteProject = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => projectsApi.deleteProject(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: PROJECTS_QUERY_KEY })

      const previousProjects = queryClient.getQueryData(PROJECTS_QUERY_KEY)

      queryClient.setQueryData(PROJECTS_QUERY_KEY, (old: ProjectsResponse | undefined) => {
        if (!old) return old
        return {
          ...old,
          items: old.items.filter((p: Project) => p.id !== id),
          total: old.total - 1,
        }
      })

      return { previousProjects }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(PROJECTS_QUERY_KEY, context.previousProjects)
      }
      toast.error(ERROR_MESSAGES.project.delete)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY })
      toast.success(SUCCESS_MESSAGES.project.deleted)
    },
  })
}
