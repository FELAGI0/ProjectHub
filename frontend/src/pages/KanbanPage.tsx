import { useParams, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { ArrowLeft, Plus, Search } from 'lucide-react'
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable'
import { useTasks, useUpdateTask } from '@/features/tasks/hooks/useTasks'
import { useDebounce } from '@/shared/hooks/useDebounce'
import type { Task, TaskStatus } from '@/features/tasks/types'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Select } from '@/shared/ui/select'
import { TaskCardSkeleton } from '@/shared/ui/skeleton'
import { KanbanColumn } from '@/features/tasks/components/KanbanColumn'
import { TaskCard } from '@/features/tasks/components/TaskCard'
import { TASK_STATUS_LABELS } from '@/shared/constants/task'

const COLUMNS: { id: TaskStatus; title: string }[] = [
  { id: 'TODO', title: TASK_STATUS_LABELS.TODO },
  { id: 'IN_PROGRESS', title: TASK_STATUS_LABELS.IN_PROGRESS },
  { id: 'DONE', title: TASK_STATUS_LABELS.DONE },
]

export function KanbanPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')
  const [activeTask, setActiveTask] = useState<Task | null>(null)
  const debouncedSearch = useDebounce(search, 500)

  const { data, isLoading, error } = useTasks(projectId || '', {
    page_size: 100,
    search: debouncedSearch || undefined,
    status: statusFilter || undefined,
    priority: priorityFilter || undefined,
  })
  const { mutate: updateTask } = useUpdateTask()

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const tasksByStatus = useMemo(() => {
    const tasks = data?.items || []
    return {
      TODO: tasks.filter((t) => t.status === 'TODO'),
      IN_PROGRESS: tasks.filter((t) => t.status === 'IN_PROGRESS'),
      DONE: tasks.filter((t) => t.status === 'DONE'),
    }
  }, [data])

  const handleDragStart = (event: DragStartEvent) => {
    const task = data?.items.find((t) => t.id === event.active.id)
    if (task) {
      setActiveTask(task)
    }
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    setActiveTask(null)

    if (!over || !projectId) return

    const taskId = active.id as string
    const newStatus = over.id as TaskStatus

    const task = data?.items.find((t) => t.id === taskId)
    if (!task || task.status === newStatus) return

    updateTask({
      taskId,
      data: { status: newStatus },
    })
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Button variant="ghost" disabled>
            <ArrowLeft className="mr-2 h-4 w-4" />
            К проекту
          </Button>
          <Button disabled>
            <Plus className="mr-2 h-4 w-4" />
            Новая задача
          </Button>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {[...Array(3)].map((_, colIdx) => (
            <div key={colIdx} className="rounded-lg border bg-card p-4 space-y-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">
                  {COLUMNS[colIdx]?.title}
                </h3>
                <div className="h-6 w-6 rounded-full bg-muted animate-pulse" />
              </div>
              <div className="space-y-3">
                {[...Array(3)].map((_, taskIdx) => (
                  <TaskCardSkeleton key={taskIdx} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}`)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К проекту
        </Button>
        <div className="rounded-lg bg-destructive/10 p-6 text-destructive">
          Не удалось загрузить задачи. Попробуйте еще раз.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}`)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К проекту
        </Button>
        <Button onClick={() => navigate(`/projects/${projectId}/tasks/new`)}>
          <Plus className="mr-2 h-4 w-4" />
          Новая задача
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Поиск задач..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Все статусы</option>
            <option value="TODO">К выполнению</option>
            <option value="IN_PROGRESS">В работе</option>
            <option value="DONE">Выполнено</option>
          </Select>
          <Select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="">Все приоритеты</option>
            <option value="LOW">Низкий</option>
            <option value="MEDIUM">Средний</option>
            <option value="HIGH">Высокий</option>
          </Select>
        </div>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="grid gap-4 md:grid-cols-3">
          {COLUMNS.map((column) => (
            <KanbanColumn
              key={column.id}
              id={column.id}
              title={column.title}
              tasks={tasksByStatus[column.id]}
              projectId={projectId || ''}
            />
          ))}
        </div>
        <DragOverlay>
          {activeTask ? <TaskCard task={activeTask} isDragging /> : null}
        </DragOverlay>
      </DndContext>
    </div>
  )
}
