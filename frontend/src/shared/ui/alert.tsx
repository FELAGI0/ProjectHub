import { type ReactNode } from 'react'
import { AlertCircle, CheckCircle2, Info, XCircle } from 'lucide-react'
import { cn } from '@/shared/utils/cn'

interface AlertProps {
  variant?: 'default' | 'destructive' | 'success' | 'warning'
  title?: string
  children: ReactNode
  className?: string
}

const variantStyles = {
  default: 'bg-muted text-foreground border-border',
  destructive: 'bg-destructive/10 text-destructive border-destructive/50',
  success: 'bg-success/10 text-success border-success/50',
  warning: 'bg-warning/10 text-warning border-warning/50',
}

const icons = {
  default: Info,
  destructive: XCircle,
  success: CheckCircle2,
  warning: AlertCircle,
}

export function Alert({ variant = 'default', title, children, className }: AlertProps) {
  const Icon = icons[variant]

  return (
    <div
      className={cn(
        'relative rounded-lg border px-4 py-3 text-sm flex gap-3',
        variantStyles[variant],
        className
      )}
    >
      <Icon className="h-5 w-5 shrink-0 mt-0.5" />
      <div className="flex-1">
        {title && <div className="font-medium mb-1">{title}</div>}
        <div>{children}</div>
      </div>
    </div>
  )
}
