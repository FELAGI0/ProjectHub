import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft, Trash2 } from 'lucide-react'
import { useProject, useUpdateProject, useDeleteProject } from '@/features/projects/hooks/useProjects'
import { projectUpdateSchema, type ProjectUpdateFormData } from '@/features/projects/schemas'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Textarea } from '@/shared/ui/textarea'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert } from '@/shared/ui/alert'
import { Skeleton } from '@/shared/ui/skeleton'
import { SuccessMessage } from '@/shared/ui/success-message'
import { FormSubmitting } from '@/shared/ui/form-submitting'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogFooter,
} from '@/shared/ui/dialog'

export function ProjectSettingsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const { data: project, isLoading } = useProject(projectId || '')
  const { mutate: updateProject, isPending: isUpdating, error: updateError } = useUpdateProject()
  const { mutate: deleteProject, isPending: isDeleting } = useDeleteProject()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProjectUpdateFormData>({
    resolver: zodResolver(projectUpdateSchema),
    values: project ? {
      name: project.name,
      description: project.description,
      is_active: project.is_active,
    } : undefined,
  })

  const onSubmit = (data: ProjectUpdateFormData) => {
    if (!projectId) return

    updateProject(
      { id: projectId, data },
      {
        onSuccess: () => {
          setSuccessMessage('Проект успешно обновлен')
          setTimeout(() => {
            navigate(`/projects/${projectId}`)
          }, 1500)
        },
      }
    )
  }

  const handleDelete = () => {
    if (!projectId) return

    deleteProject(projectId, {
      onSuccess: () => {
        navigate('/projects')
      },
    })
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

  if (!project) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Button variant="ghost" onClick={() => navigate('/projects')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К проектам
        </Button>
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">
              Не удалось загрузить проект. Попробуйте еще раз.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}`)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        К проекту
      </Button>

      <div>
        <h1 className="text-3xl font-bold">Настройки проекта</h1>
        <p className="text-muted-foreground mt-1">
          Управляйте настройками проекта
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Основные настройки</CardTitle>
          <CardDescription>
            Обновите информацию о проекте
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

            {updateError && (
              <Alert variant="destructive">
                Не удалось обновить проект. Попробуйте еще раз.
              </Alert>
            )}

            {isUpdating && (
              <FormSubmitting message="Сохранение проекта..." />
            )}

            <div className="space-y-2">
              <Label htmlFor="name" required>
                Название проекта
              </Label>
              <Input
                id="name"
                placeholder="Мой проект"
                {...register('name')}
                disabled={isUpdating}
              />
              {errors.name && (
                <p className="text-sm text-destructive">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">
                Описание
              </Label>
              <Textarea
                id="description"
                placeholder="Описание проекта..."
                rows={4}
                {...register('description')}
                disabled={isUpdating}
              />
              {errors.description && (
                <p className="text-sm text-destructive">{errors.description.message}</p>
              )}
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="is_active"
                className="h-4 w-4 rounded border-gray-300"
                {...register('is_active')}
                disabled={isUpdating}
              />
              <label htmlFor="is_active" className="text-sm font-medium">
                Активный проект
              </label>
            </div>

            <div className="flex items-center gap-3 pt-4">
              <Button type="submit" disabled={isUpdating}>
                {isUpdating ? 'Сохранение...' : 'Сохранить изменения'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate(`/projects/${projectId}`)}
                disabled={isUpdating}
              >
                Отмена
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Опасная зона</CardTitle>
          <CardDescription>
            Необратимые и разрушительные действия
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Удалить проект</p>
              <p className="text-sm text-muted-foreground">
                Навсегда удалить этот проект и все его задачи
              </p>
            </div>
            <Button
              variant="destructive"
              onClick={() => setShowDeleteDialog(true)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Удалить
            </Button>
          </div>
        </CardContent>
      </Card>

      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader onClose={() => setShowDeleteDialog(false)}>
            <DialogTitle>Удаление проекта</DialogTitle>
            <DialogDescription>
              Вы уверены, что хотите удалить этот проект?
            </DialogDescription>
          </DialogHeader>
          <DialogBody>
            <p className="text-sm">
              Это действие нельзя отменить. Проект <strong>{project.name}</strong> и все его задачи будут удалены навсегда.
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
              {isDeleting ? 'Удаление...' : 'Удалить проект'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
