
import { useDroppable } from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import type { Task } from '../types'
import { TaskCard } from './TaskCard'
import { EmptyState } from '@/shared/ui/empty-state'
import { ListTodo } from 'lucide-react'
import { cn } from '@/shared/utils/cn'

interface KanbanColumnProps {
  id: string
  title: string
  tasks: Task[]
  projectId: string
}

export function KanbanColumn({ id, title, tasks, projectId }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id })

  return (
    <div className="flex flex-col gap-2.5">
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'h-1.5 w-1.5 rounded-full',
              id === 'TODO' && 'bg-muted-foreground/50',
              id === 'IN_PROGRESS' && 'bg-blue-500/70',
              id === 'DONE' && 'bg-success/80'
            )}
          />
          <h3 className="text-sm font-semibold tracking-tight">{title}</h3>
        </div>
        <span className="rounded border border-border/70 bg-secondary/60 px-1.5 py-0.5 text-xs font-medium tabular-nums text-muted-foreground">
          {tasks.length}
        </span>
      </div>

      <div
        ref={setNodeRef}
        className={cn(
          'flex min-h-[420px] flex-col gap-2 rounded-xl border bg-secondary/30 p-3 transition-colors',
          isOver
            ? 'border-primary/40 bg-primary/5'
            : 'border-border/60 hover:border-border'
        )}
      >
        <SortableContext
          items={tasks.map((t) => t.id)}
          strategy={verticalListSortingStrategy}
        >
          {tasks.length === 0 ? (
            <div className="flex items-center justify-center py-10">
              <EmptyState
                icon={<ListTodo className="h-6 w-6" />}
                title="Нет задач"
                description="В этой колонке пока нет задач"
                className="py-0"
              />
            </div>
          ) : (
            tasks.map((task) => (
              <TaskCard key={task.id} task={task} projectId={projectId} />
            ))
          )}
        </SortableContext>
      </div>
    </div>
  )
}
