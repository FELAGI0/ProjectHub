export type MemberRole = 'owner' | 'admin' | 'member'

export interface Member {
  id: string
  project_id: string
  user_id: string
  role: MemberRole
  joined_at: string
}

export interface MemberAddRequest {
  user_id: string
  role?: MemberRole
}

export interface MemberUpdateRequest {
  role: MemberRole
}
