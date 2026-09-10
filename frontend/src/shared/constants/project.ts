export const PROJECT_ROLES = {
  OWNER: 'OWNER',
  ADMIN: 'ADMIN',
  MEMBER: 'MEMBER',
} as const

export type ProjectRole = keyof typeof PROJECT_ROLES

export const PROJECT_ROLE_LABELS: Record<ProjectRole, string> = {
  OWNER: 'Владелец',
  ADMIN: 'Администратор',
  MEMBER: 'Участник',
}

export const PROJECT_ROLE_COLORS: Record<ProjectRole, string> = {
  OWNER: 'text-purple-600 bg-purple-50 border-purple-200 dark:text-purple-400 dark:bg-purple-950 dark:border-purple-800',
  ADMIN: 'text-blue-600 bg-blue-50 border-blue-200 dark:text-blue-400 dark:bg-blue-950 dark:border-blue-800',
  MEMBER: 'text-gray-600 bg-gray-50 border-gray-200 dark:text-gray-400 dark:bg-gray-950 dark:border-gray-800',
}

export const PROJECT_ROLE_PERMISSIONS = {
  OWNER: ['read', 'write', 'delete', 'manage_members', 'manage_settings'],
  ADMIN: ['read', 'write', 'manage_members'],
  MEMBER: ['read'],
} as const
