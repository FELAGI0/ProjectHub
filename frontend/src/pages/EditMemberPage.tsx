import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft } from 'lucide-react'
import { z } from 'zod'
import { useUpdateMemberRole } from '@/features/project-members/hooks/useProjectMembers'
import { useProject } from '@/features/projects/hooks/useProjects'
import { Button } from '@/shared/ui/button'
import { Select } from '@/shared/ui/select'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert } from '@/shared/ui/alert'
import { SuccessMessage } from '@/shared/ui/success-message'
import { FormSubmitting } from '@/shared/ui/form-submitting'

const editMemberSchema = z.object({
  role: z.enum(['MEMBER', 'ADMIN'] as const),
})

type EditMemberFormData = z.infer<typeof editMemberSchema>

export function EditMemberPage() {
  const { projectId, userId } = useParams<{ projectId: string; userId: string }>()
  const navigate = useNavigate()
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const { data: project } = useProject(projectId || '')
  const { mutate: updateMemberRole, isPending, error } = useUpdateMemberRole()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EditMemberFormData>({
    resolver: zodResolver(editMemberSchema),
    defaultValues: {
      role: 'MEMBER',
    },
  })

  const onSubmit = (data: EditMemberFormData) => {
    if (!projectId || !userId) return

    updateMemberRole(
      {
        projectId,
        userId,
        data: { role: data.role },
      },
      {
        onSuccess: () => {
          setSuccessMessage('Роль участника успешно изменена')
          setTimeout(() => {
            navigate(`/projects/${projectId}/team`)
          }, 1500)
        },
      }
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}/team`)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        К команде
      </Button>

      <div>
        <h1 className="text-3xl font-bold">Изменение роли участника</h1>
        <p className="text-muted-foreground mt-1">
          Измените роль участника в проекте {project?.name}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Новая роль</CardTitle>
          <CardDescription>
            Выберите новую роль для этого участника
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
                Не удалось изменить роль. Попробуйте еще раз.
              </Alert>
            )}

            {isPending && (
              <FormSubmitting message="Изменение роли..." />
            )}

            <div className="space-y-2">
              <Label htmlFor="role">
                Роль
              </Label>
              <Select id="role" {...register('role')} disabled={isPending}>
                <option value="MEMBER">Участник</option>
                <option value="ADMIN">Администратор</option>
              </Select>
              {errors.role && (
                <p className="text-sm text-destructive">{errors.role.message}</p>
              )}
            </div>

            <div className="flex items-center gap-3 pt-4">
              <Button type="submit" disabled={isPending}>
                {isPending ? 'Изменение...' : 'Сохранить'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate(`/projects/${projectId}/team`)}
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
