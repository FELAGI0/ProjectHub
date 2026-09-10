import { useDroppable } from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import type { Task } from '../types'
import { TaskCard } from './TaskCard'
import { EmptyState } from '@/shared/ui/empty-state'
import { ListTodo } from 'lucide-react'

interface KanbanColumnProps {
  id: string
  title: string
  tasks: Task[]
  projectId: string
}

export function KanbanColumn({ id, title, tasks, projectId }: KanbanColumnProps) {
  const { setNodeRef } = useDroppable({ id })

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between px-2">
        <h3 className="font-semibold">{title}</h3>
        <span className="text-sm text-muted-foreground">{tasks.length}</span>
      </div>

      <div
        ref={setNodeRef}
        className="flex flex-col gap-2 min-h-[400px] rounded-lg border-2 border-dashed border-border bg-accent/5 p-3 transition-colors hover:border-primary/30"
      >
        <SortableContext
          items={tasks.map((t) => t.id)}
          strategy={verticalListSortingStrategy}
        >
          {tasks.length === 0 ? (
            <div className="flex items-center justify-center h-32">
              <EmptyState
                icon={<ListTodo className="h-8 w-8" />}
                title="Нет задач"
                description="В этой колонке пока нет задач"
                className="py-4"
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
