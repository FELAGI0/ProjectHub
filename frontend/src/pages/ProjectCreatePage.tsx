import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useCreateProject } from '@/features/projects/hooks/useProjects'
import { projectCreateSchema, type ProjectCreateFormData } from '@/features/projects/schemas'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Textarea } from '@/shared/ui/textarea'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert } from '@/shared/ui/alert'
import { SuccessMessage } from '@/shared/ui/success-message'
import { FormSubmitting } from '@/shared/ui/form-submitting'

export function ProjectCreatePage() {
  const navigate = useNavigate()
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const { mutate: createProject, isPending, error } = useCreateProject()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProjectCreateFormData>({
    resolver: zodResolver(projectCreateSchema),
  })

  const onSubmit = (data: ProjectCreateFormData) => {
    createProject(data, {
      onSuccess: (project) => {
        setSuccessMessage(`Проект "${project.name}" успешно создан`)
        setTimeout(() => {
          navigate(`/projects/${project.id}`)
        }, 1500)
      },
    })
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Создание проекта</h1>
        <p className="text-muted-foreground mt-1">
          Создайте новый проект для организации задач
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Информация о проекте</CardTitle>
          <CardDescription>
            Введите основные данные для нового проекта
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
                Не удалось создать проект. Попробуйте еще раз.
              </Alert>
            )}

            {isPending && (
              <FormSubmitting message="Создание проекта..." />
            )}

            <div className="space-y-2">
              <Label htmlFor="name" required>
                Название проекта
              </Label>
              <Input
                id="name"
                placeholder="Мой проект"
                {...register('name')}
                disabled={isPending}
              />
              {errors.name && (
                <Alert variant="destructive">
                  {errors.name.message}
                </Alert>
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
                disabled={isPending}
              />
              {errors.description && (
                <Alert variant="destructive">
                  {errors.description.message}
                </Alert>
              )}
            </div>

            <div className="flex items-center gap-3 pt-4">
              <Button type="submit" disabled={isPending}>
                {isPending ? 'Создание...' : 'Создать проект'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/projects')}
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
