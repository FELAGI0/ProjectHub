import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { authApi } from '../api/authApi'
import { useAuthStore } from '../store/authStore'
import type { LoginRequest, RegisterRequest } from '../types'
import { SUCCESS_MESSAGES, ERROR_MESSAGES } from '@/shared/constants/messages'

export const useLogin = () => {
  const setAuth = useAuthStore((state) => state.setAuth)

  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      setAuth(
        response.user,
        response.tokens.access_token,
        response.tokens.refresh_token
      )
      toast.success(SUCCESS_MESSAGES.auth.login)
    },
    onError: () => {
      toast.error(ERROR_MESSAGES.auth.login)
    },
  })
}

export const useRegister = () => {
  const setAuth = useAuthStore((state) => state.setAuth)

  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      setAuth(
        response.user,
        response.tokens.access_token,
        response.tokens.refresh_token
      )
      toast.success(SUCCESS_MESSAGES.auth.register)
    },
    onError: () => {
      toast.error(ERROR_MESSAGES.auth.register)
    },
  })
}

export const useLogout = () => {
  const clearAuth = useAuthStore((state) => state.clearAuth)

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      clearAuth()
      toast.success(SUCCESS_MESSAGES.auth.logout)
    },
    onError: () => {
      toast.error(ERROR_MESSAGES.auth.logout)
    },
  })
}
