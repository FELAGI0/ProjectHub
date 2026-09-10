import { X } from 'lucide-react'
import { cn } from '@/shared/utils/cn'
import { Button } from './button'

interface ToastProps {
  variant?: 'default' | 'success' | 'error' | 'warning'
  title?: string
  message: string
  onClose?: () => void
  className?: string
}

const variantStyles = {
  default: 'bg-card border-border',
  success: 'bg-success/10 border-success/50 text-success',
  error: 'bg-destructive/10 border-destructive/50 text-destructive',
  warning: 'bg-warning/10 border-warning/50 text-warning',
}

export function Toast({ variant = 'default', title, message, onClose, className }: ToastProps) {
  return (
    <div
      className={cn(
        'rounded-lg border shadow-lg p-4 animate-in fade-in-0 slide-in-from-right-5 duration-300',
        variantStyles[variant],
        className
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex-1">
          {title && <div className="font-medium mb-1">{title}</div>}
          <div className="text-sm">{message}</div>
        </div>
        {onClose && (
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 shrink-0"
            onClick={onClose}
            aria-label="Закрыть"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  )
}
