import { type ReactNode } from 'react'
import { Loader2 } from 'lucide-react'
import { cn } from '@/shared/utils/cn'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <Loader2
      className={cn('animate-spin text-muted-foreground', sizeClasses[size], className)}
    />
  )
}

interface LoadingStateProps {
  message?: string
  children?: ReactNode
}

export function LoadingState({ message = 'Загрузка...', children }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <Spinner size="lg" />
      {children || <p className="text-sm text-muted-foreground">{message}</p>}
    </div>
  )
}
