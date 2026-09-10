import { z } from 'zod'
import { VALIDATION_MESSAGES } from '@/shared/constants/messages'

export const loginSchema = z.object({
  email: z.string().email(VALIDATION_MESSAGES.email),
  password: z.string().min(1, VALIDATION_MESSAGES.password.required),
})

export const registerSchema = z.object({
  email: z.string().email(VALIDATION_MESSAGES.email),
  username: z
    .string()
    .min(3, VALIDATION_MESSAGES.username.minLength)
    .max(50, VALIDATION_MESSAGES.maxLength(50))
    .regex(
      /^[a-z0-9][a-z0-9_-]*$/,
      'Имя пользователя должно начинаться с буквы или цифры и содержать только строчные буквы, цифры, дефисы и подчеркивания'
    ),
  password: z
    .string()
    .min(12, VALIDATION_MESSAGES.password.minLength)
    .max(128, VALIDATION_MESSAGES.maxLength(128)),
})

export type LoginFormData = z.infer<typeof loginSchema>
export type RegisterFormData = z.infer<typeof registerSchema>
