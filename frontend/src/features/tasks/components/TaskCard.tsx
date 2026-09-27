
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
    opacity: isSortableDragging ? 0.45 : 1,
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
        'group rounded-xl border border-border/70 bg-card p-3.5 shadow-sm transition-[border-color,box-shadow,transform] duration-200 hover:border-border hover:shadow-md active:cursor-grabbing',
        isDragging && 'scale-[1.03] border-primary/50 shadow-lg'
      )}
      onClick={handleClick}
    >
      <div className="space-y-2.5">
        <div className="flex items-start justify-between gap-2.5">
          <h4 className="line-clamp-2 text-sm font-medium leading-snug">{task.title}</h4>
          <Badge
            variant="outline"
            className={cn('shrink-0 text-[0.6875rem]', TASK_PRIORITY_COLORS[task.priority])}
          >
            {TASK_PRIORITY_LABELS[task.priority]}
          </Badge>
        </div>

        {task.description && (
          <p className="line-clamp-2 text-xs leading-relaxed text-muted-foreground">
            {task.description}
          </p>
        )}

        {dueDate && (
          <div
            className={cn(
              'flex items-center gap-1.5 text-[0.6875rem] font-medium',
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
