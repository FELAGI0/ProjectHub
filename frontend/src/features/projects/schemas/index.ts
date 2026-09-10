import { z } from 'zod'
import { VALIDATION_MESSAGES } from '@/shared/constants/messages'

export const projectCreateSchema = z.object({
  name: z
    .string()
    .min(1, 'Название проекта обязательно')
    .max(100, VALIDATION_MESSAGES.maxLength(100)),
  description: z
    .string()
    .max(500, VALIDATION_MESSAGES.maxLength(500))
    .optional()
    .nullable(),
})

export const projectUpdateSchema = z.object({
  name: z
    .string()
    .min(1, 'Название проекта обязательно')
    .max(100, VALIDATION_MESSAGES.maxLength(100))
    .optional(),
  description: z
    .string()
    .max(500, VALIDATION_MESSAGES.maxLength(500))
    .optional()
    .nullable(),
  is_active: z.boolean().optional(),
})

export type ProjectCreateFormData = z.infer<typeof projectCreateSchema>
export type ProjectUpdateFormData = z.infer<typeof projectUpdateSchema>
