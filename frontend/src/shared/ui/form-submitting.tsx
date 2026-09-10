import { type ReactNode } from 'react'
import { Loader2 } from 'lucide-react'
import { cn } from '@/shared/utils/cn'

interface FormSubmittingProps {
  message?: string
  children?: ReactNode
  className?: string
}

export function FormSubmitting({ message = 'Сохранение...', children, className }: FormSubmittingProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-primary/50 bg-primary/10 p-4 animate-in fade-in-0 duration-200',
        className
      )}
    >
      <div className="flex items-center gap-3">
        <Loader2 className="h-5 w-5 text-primary animate-spin shrink-0" />
        <div className="flex-1">
          {children || <p className="text-sm text-primary font-medium">{message}</p>}
        </div>
      </div>
    </div>
  )
}
