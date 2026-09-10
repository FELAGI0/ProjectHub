import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Calendar, Edit2, Trash2, AlertCircle } from 'lucide-react'
import { useTask, useDeleteTask } from '@/features/tasks/hooks/useTasks'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Skeleton } from '@/shared/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogFooter,
} from '@/shared/ui/dialog'
import { cn } from '@/shared/utils/cn'
import { TASK_STATUS_LABELS, TASK_PRIORITY_LABELS, TASK_PRIORITY_COLORS } from '@/shared/constants/task'

export function TaskDetailPage() {
  const { projectId, taskId } = useParams<{ projectId: string; taskId: string }>()
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const { data: task, isLoading, error } = useTask(taskId || '')
  const { mutate: deleteTask, isPending: isDeleting } = useDeleteTask()

  const handleDelete = () => {
    if (!taskId || !projectId) return

    deleteTask(
      { taskId, projectId },
      {
        onSuccess: () => {
          navigate(`/projects/${projectId}/kanban`)
        },
      }
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-48" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !task) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}`)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К проекту
        </Button>
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">
              Не удалось загрузить задачу. Попробуйте еще раз.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const dueDate = task.due_date ? new Date(task.due_date) : null
  const isOverdue = dueDate && dueDate < new Date() && task.status !== 'DONE'

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}/kanban`)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К Kanban-доске
        </Button>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => navigate(`/projects/${projectId}/tasks/${taskId}/edit`)}
          >
            <Edit2 className="mr-2 h-4 w-4" />
            Редактировать
          </Button>
          <Button variant="destructive" onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="mr-2 h-4 w-4" />
            Удалить
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <CardTitle className="text-2xl">{task.title}</CardTitle>
              </div>
              <Badge
                variant="secondary"
                className={cn(TASK_PRIORITY_COLORS[task.priority])}
              >
                {TASK_PRIORITY_LABELS[task.priority]}
              </Badge>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline">{TASK_STATUS_LABELS[task.status]}</Badge>
              {dueDate && (
                <div
                  className={cn(
                    'flex items-center gap-1 text-sm',
                    isOverdue ? 'text-destructive' : 'text-muted-foreground'
                  )}
                >
                  {isOverdue ? (
                    <AlertCircle className="h-4 w-4" />
                  ) : (
                    <Calendar className="h-4 w-4" />
                  )}
                  <span>
                    Срок: {dueDate.toLocaleDateString('ru-RU')}
                    {isOverdue && ' (просрочено)'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="font-semibold mb-2">Описание</h3>
            <p className="text-muted-foreground whitespace-pre-wrap">
              {task.description || 'Без описания'}
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="text-sm font-medium mb-1">Создана</h4>
              <p className="text-sm text-muted-foreground">
                {new Date(task.created_at).toLocaleString('ru-RU')}
              </p>
            </div>
            <div>
              <h4 className="text-sm font-medium mb-1">Обновлена</h4>
              <p className="text-sm text-muted-foreground">
                {new Date(task.updated_at).toLocaleString('ru-RU')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader onClose={() => setShowDeleteDialog(false)}>
            <DialogTitle>Удаление задачи</DialogTitle>
            <DialogDescription>
              Вы уверены, что хотите удалить эту задачу?
            </DialogDescription>
          </DialogHeader>
          <DialogBody>
            <p className="text-sm">
              Это действие нельзя отменить. Задача <strong>{task.title}</strong> будет удалена навсегда.
            </p>
          </DialogBody>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={isDeleting}
            >
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? 'Удаление...' : 'Удалить задачу'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
