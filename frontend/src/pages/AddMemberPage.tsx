import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { z } from 'zod'
import { useAddMember } from '@/features/project-members/hooks/useProjectMembers'
import { useProject } from '@/features/projects/hooks/useProjects'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Select } from '@/shared/ui/select'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert } from '@/shared/ui/alert'
import { SuccessMessage } from '@/shared/ui/success-message'
import { FormSubmitting } from '@/shared/ui/form-submitting'

const addMemberSchema = z.object({
  user_id: z.string().uuid('Некорректный ID пользователя'),
  role: z.enum(['MEMBER', 'ADMIN'] as const),
})

type AddMemberFormData = z.infer<typeof addMemberSchema>

export function AddMemberPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const { data: project } = useProject(projectId || '')
  const { mutate: addMember, isPending, error } = useAddMember()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AddMemberFormData>({
    resolver: zodResolver(addMemberSchema),
    defaultValues: {
      role: 'MEMBER',
    },
  })

  const onSubmit = (data: AddMemberFormData) => {
    if (!projectId) return

    addMember(
      { projectId, data },
      {
        onSuccess: () => {
          setSuccessMessage('Участник успешно добавлен')
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
        <h1 className="text-3xl font-bold">Добавление участника</h1>
        <p className="text-muted-foreground mt-1">
          Добавьте нового участника в проект {project?.name}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Информация об участнике</CardTitle>
          <CardDescription>
            Укажите ID пользователя и роль
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
                Не удалось добавить участника. Попробуйте еще раз.
              </Alert>
            )}

            {isPending && (
              <FormSubmitting message="Добавление участника..." />
            )}

            <div className="space-y-2">
              <Label htmlFor="user_id" required>
                ID пользователя
              </Label>
              <Input
                id="user_id"
                placeholder="Введите UUID пользователя"
                {...register('user_id')}
                disabled={isPending}
              />
              {errors.user_id && (
                <p className="text-sm text-destructive">{errors.user_id.message}</p>
              )}
            </div>

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
                {isPending ? 'Добавление...' : 'Добавить участника'}
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
