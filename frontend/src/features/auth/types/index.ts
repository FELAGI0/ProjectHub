export interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  access_token_expires_in: number
}

export interface AuthResponse {
  user: User
  tokens: TokenPair
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}
