import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { useTask, useUpdateTask } from '@/features/tasks/hooks/useTasks'
import { taskUpdateSchema, type TaskUpdateFormData } from '@/features/tasks/schemas'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Select } from '@/shared/ui/select'
import { Textarea } from '@/shared/ui/textarea'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert } from '@/shared/ui/alert'
import { Skeleton } from '@/shared/ui/skeleton'
import { SuccessMessage } from '@/shared/ui/success-message'
import { FormSubmitting } from '@/shared/ui/form-submitting'

export function TaskEditPage() {
  const { projectId, taskId } = useParams<{ projectId: string; taskId: string }>()
  const navigate = useNavigate()
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const { data: task, isLoading } = useTask(taskId || '')
  const { mutate: updateTask, isPending, error } = useUpdateTask()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskUpdateFormData>({
    resolver: zodResolver(taskUpdateSchema),
    values: task ? {
      title: task.title,
      description: task.description,
      status: task.status,
      priority: task.priority,
      due_date: task.due_date ? task.due_date.split('T')[0] : null,
    } : undefined,
  })

  const onSubmit = (data: TaskUpdateFormData) => {
    if (!taskId) return

    updateTask(
      { taskId, data },
      {
        onSuccess: () => {
          setSuccessMessage('Задача успешно обновлена')
          setTimeout(() => {
            navigate(`/projects/${projectId}/tasks/${taskId}`)
          }, 1500)
        },
      }
    )
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Skeleton className="h-10 w-64" />
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-24 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!task) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
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

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}/tasks/${taskId}`)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        К задаче
      </Button>

      <div>
        <h1 className="text-3xl font-bold">Редактирование задачи</h1>
        <p className="text-muted-foreground mt-1">
          Обновите информацию о задаче
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Информация о задаче</CardTitle>
          <CardDescription>
            Измените данные задачи
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {successMessage && (
              <SuccessMessage
                title="Успешно"
                message={successMessage}
              />
            )}

            {error && (
              <Alert variant="destructive">
                Не удалось обновить задачу. Попробуйте еще раз.
              </Alert>
            )}

            {isPending && (
              <FormSubmitting message="Сохранение задачи..." />
            )}

            <div className="space-y-2">
              <Label htmlFor="title" required>
                Название
              </Label>
              <Input
                id="title"
                placeholder="Название задачи"
                {...register('title')}
                disabled={isPending}
              />
              {errors.title && (
                <p className="text-sm text-destructive">{errors.title.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">
                Описание
              </Label>
              <Textarea
                id="description"
                placeholder="Описание задачи..."
                rows={4}
                {...register('description')}
                disabled={isPending}
              />
              {errors.description && (
                <p className="text-sm text-destructive">
                  {errors.description.message}
                </p>
              )}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="status">
                  Статус
                </Label>
                <Select id="status" {...register('status')} disabled={isPending}>
                  <option value="TODO">К выполнению</option>
                  <option value="IN_PROGRESS">В работе</option>
                  <option value="DONE">Выполнено</option>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="priority">
                  Приоритет
                </Label>
                <Select id="priority" {...register('priority')} disabled={isPending}>
                  <option value="LOW">Низкий</option>
                  <option value="MEDIUM">Средний</option>
                  <option value="HIGH">Высокий</option>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="due_date">
                Срок выполнения
              </Label>
              <Input
                id="due_date"
                type="date"
                {...register('due_date')}
                disabled={isPending}
              />
            </div>

            <div className="flex items-center gap-3 pt-4">
              <Button type="submit" disabled={isPending}>
                {isPending ? 'Сохранение...' : 'Сохранить изменения'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate(`/projects/${projectId}/tasks/${taskId}`)}
                disabled={isPending}
              >
                Отмена
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
