import { z } from 'zod'
import { VALIDATION_MESSAGES } from '@/shared/constants/messages'

export const taskCreateSchema = z.object({
  title: z
    .string()
    .min(1, 'Название задачи обязательно')
    .max(200, VALIDATION_MESSAGES.maxLength(200)),
  description: z
    .string()
    .max(2000, VALIDATION_MESSAGES.maxLength(2000))
    .optional()
    .nullable(),
  status: z.enum(['TODO', 'IN_PROGRESS', 'DONE']).optional(),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH']).optional(),
  due_date: z.string().nullable().optional(),
})

export const taskUpdateSchema = z.object({
  title: z
    .string()
    .min(1, 'Название задачи обязательно')
    .max(200, VALIDATION_MESSAGES.maxLength(200))
    .optional(),
  description: z
    .string()
    .max(2000, VALIDATION_MESSAGES.maxLength(2000))
    .optional()
    .nullable(),
  status: z.enum(['TODO', 'IN_PROGRESS', 'DONE']).optional(),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH']).optional(),
  due_date: z.string().nullable().optional(),
})

export type TaskCreateFormData = z.infer<typeof taskCreateSchema>
export type TaskUpdateFormData = z.infer<typeof taskUpdateSchema>
