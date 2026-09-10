import { type ReactNode } from 'react'
import { CheckCircle2 } from 'lucide-react'
import { cn } from '@/shared/utils/cn'

interface SuccessMessageProps {
  title?: string
  message: string
  action?: ReactNode
  className?: string
}

export function SuccessMessage({ title, message, action, className }: SuccessMessageProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-success/50 bg-success/10 p-4 animate-in fade-in-0 zoom-in-95 duration-200',
        className
      )}
    >
      <div className="flex gap-3">
        <CheckCircle2 className="h-5 w-5 text-success shrink-0 mt-0.5" />
        <div className="flex-1">
          {title && <div className="font-medium text-success mb-1">{title}</div>}
          <div className="text-sm text-success">{message}</div>
          {action && <div className="mt-3">{action}</div>}
        </div>
      </div>
    </div>
  )
}
