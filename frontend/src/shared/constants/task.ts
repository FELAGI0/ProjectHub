export const TASK_STATUSES = {
  TODO: 'TODO',
  IN_PROGRESS: 'IN_PROGRESS',
  DONE: 'DONE',
} as const

export const TASK_PRIORITIES = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
} as const

export type TaskStatus = keyof typeof TASK_STATUSES
export type TaskPriority = keyof typeof TASK_PRIORITIES

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  TODO: 'К выполнению',
  IN_PROGRESS: 'В работе',
  DONE: 'Выполнено',
}

export const TASK_PRIORITY_LABELS: Record<TaskPriority, string> = {
  LOW: 'Низкий',
  MEDIUM: 'Средний',
  HIGH: 'Высокий',
}

export const TASK_PRIORITY_COLORS: Record<TaskPriority, string> = {
  LOW: 'border-blue-500/25 bg-blue-500/10 text-blue-600 dark:text-blue-400',
  MEDIUM: 'border-yellow-500/25 bg-yellow-500/10 text-yellow-700 dark:text-yellow-400',
  HIGH: 'border-red-500/25 bg-red-500/10 text-red-600 dark:text-red-400',
}

export const TASK_STATUS_COLORS: Record<TaskStatus, string> = {
  TODO: 'border-border bg-secondary/60 text-muted-foreground',
  IN_PROGRESS: 'border-blue-500/25 bg-blue-500/10 text-blue-600 dark:text-blue-400',
  DONE: 'border-success/25 bg-success/10 text-success',
}
