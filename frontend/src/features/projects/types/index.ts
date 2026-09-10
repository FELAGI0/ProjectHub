export interface Project {
  id: string
  name: string
  description: string | null
  owner_id: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProjectCreateRequest {
  name: string
  description?: string | null
}

export interface ProjectUpdateRequest {
  name?: string
  description?: string | null
  is_active?: boolean
}
