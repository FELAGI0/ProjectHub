
import { forwardRef, type SelectHTMLAttributes } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/shared/utils/cn'

export type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  error?: boolean
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, error, ...props }, ref) => {
    return (
      <div className={cn('relative', className)}>
        <select
          className={cn(
            'h-10 w-full appearance-none rounded-lg border border-input bg-card/70 px-3 pr-9 text-sm text-foreground shadow-sm transition-[border-color,box-shadow] focus-visible:border-primary/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/25 focus-visible:ring-offset-1 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-55',
            error && 'border-destructive/70 focus-visible:ring-destructive/25'
          )}
          ref={ref}
          {...props}
        >
          {children}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      </div>
    )
  }
)
Select.displayName = 'Select'

export { Select }
