import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { useCreateTask } from '@/features/tasks/hooks/useTasks'
import { taskCreateSchema, type TaskCreateFormData } from '@/features/tasks/schemas'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Select } from '@/shared/ui/select'
import { Textarea } from '@/shared/ui/textarea'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert } from '@/shared/ui/alert'
import { SuccessMessage } from '@/shared/ui/success-message'
import { FormSubmitting } from '@/shared/ui/form-submitting'

export function TaskCreatePage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const { mutate: createTask, isPending, error } = useCreateTask()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskCreateFormData>({
    resolver: zodResolver(taskCreateSchema),
    defaultValues: {
      status: 'TODO',
      priority: 'MEDIUM',
    },
  })

  const onSubmit = (data: TaskCreateFormData) => {
    if (!projectId) return

    createTask(
      { projectId, data },
      {
        onSuccess: () => {
          setSuccessMessage('Задача успешно создана')
          setTimeout(() => {
            navigate(`/projects/${projectId}/kanban`)
          }, 1500)
        },
      }
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}`)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        К проекту
      </Button>

      <div>
        <h1 className="text-3xl font-bold">Создание задачи</h1>
        <p className="text-muted-foreground mt-1">
          Добавьте новую задачу в проект
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Информация о задаче</CardTitle>
          <CardDescription>
            Введите данные для новой задачи
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
                Не удалось создать задачу. Попробуйте еще раз.
              </Alert>
            )}

            {isPending && (
              <FormSubmitting message="Создание задачи..." />
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
              <label htmlFor="due_date" className="text-sm font-medium">
                Срок выполнения
              </label>
              <Input
                id="due_date"
                type="date"
                {...register('due_date')}
                disabled={isPending}
              />
            </div>

            <div className="flex items-center gap-3 pt-4">
              <Button type="submit" disabled={isPending}>
                {isPending ? 'Создание...' : 'Создать задачу'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate(`/projects/${projectId}`)}
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
