export interface ProjectMember {
  id: string
  project_id: string
  user_id: string
  role: ProjectRole
  created_at: string
  updated_at: string
  user: {
    id: string
    email: string
    username: string
  }
}

export type ProjectRole = 'MEMBER' | 'ADMIN' | 'OWNER'

export interface MemberAddRequest {
  user_id: string
  role?: ProjectRole
}

export interface MemberRoleUpdateRequest {
  role: ProjectRole
}
