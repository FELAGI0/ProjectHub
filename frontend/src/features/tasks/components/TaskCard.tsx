import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useNavigate } from 'react-router-dom'
import { Calendar, AlertCircle } from 'lucide-react'
import type { Task } from '../types'
import { Badge } from '@/shared/ui/badge'
import { cn } from '@/shared/utils/cn'
import { TASK_PRIORITY_LABELS, TASK_PRIORITY_COLORS } from '@/shared/constants/task'

interface TaskCardProps {
  task: Task
  projectId?: string
  isDragging?: boolean
}

export function TaskCard({ task, projectId, isDragging }: TaskCardProps) {
  const navigate = useNavigate()
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: task.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isSortableDragging ? 0.5 : 1,
  }

  const handleClick = () => {
    if (projectId) {
      navigate(`/projects/${projectId}/tasks/${task.id}`)
    }
  }

  const dueDate = task.due_date ? new Date(task.due_date) : null
  const isOverdue = dueDate && dueDate < new Date() && task.status !== 'DONE'

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={cn(
        'rounded-lg border border-border bg-background p-3 cursor-grab active:cursor-grabbing hover:shadow-lg hover:scale-[1.02] transition-all duration-200',
        isDragging && 'shadow-xl ring-2 ring-primary scale-105'
      )}
      onClick={handleClick}
    >
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h4 className="font-medium text-sm line-clamp-2">{task.title}</h4>
          <Badge
            variant="secondary"
            className={cn('shrink-0 text-xs', TASK_PRIORITY_COLORS[task.priority])}
          >
            {TASK_PRIORITY_LABELS[task.priority]}
          </Badge>
        </div>

        {task.description && (
          <p className="text-xs text-muted-foreground line-clamp-2">
            {task.description}
          </p>
        )}

        {dueDate && (
          <div
            className={cn(
              'flex items-center gap-1 text-xs',
              isOverdue ? 'text-destructive' : 'text-muted-foreground'
            )}
          >
            {isOverdue ? (
              <AlertCircle className="h-3 w-3" />
            ) : (
              <Calendar className="h-3 w-3" />
            )}
            <span>
              {dueDate.toLocaleDateString('ru-RU', {
                month: 'short',
                day: 'numeric',
              })}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
