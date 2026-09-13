import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { z } from 'zod'
import { useAuthStore } from '@/features/auth/store/authStore'
import { authApi } from '@/features/auth/api/authApi'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert } from '@/shared/ui/alert'
import { SuccessMessage } from '@/shared/ui/success-message'
import { FormSubmitting } from '@/shared/ui/form-submitting'

const userSettingsSchema = z.object({
  username: z.string().min(1, 'Имя пользователя обязательно'),
  email: z.string().email('Некорректный email'),
})

type UserSettingsFormData = z.infer<typeof userSettingsSchema>

export function UserSettingsPage() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const setUser = useAuthStore((state) => state.setUser)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UserSettingsFormData>({
    resolver: zodResolver(userSettingsSchema),
    values: user ? {
      username: user.username,
      email: user.email,
    } : undefined,
  })

  const onSubmit = async (data: UserSettingsFormData) => {
    setIsSubmitting(true)
    setError(null)

    try {
      const updated = await authApi.updateProfile({
        username: data.username,
        email: data.email,
      })
      setUser(updated)
      setSuccessMessage('Настройки успешно сохранены')
      setTimeout(() => {
        navigate('/')
      }, 1500)
    } catch (err) {
      setError('Не удалось сохранить настройки. Попробуйте еще раз.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!user) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">Настройки</h1>
          <p className="text-muted-foreground">
            Перенаправляем на главную...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Настройки профиля</h1>
        <p className="text-muted-foreground mt-1">
          Управляйте информацией своего профиля
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Основные сведения</CardTitle>
          <CardDescription>
            Обновите информацию о вашем профиле
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
                {error}
              </Alert>
            )}

            {isSubmitting && (
              <FormSubmitting message="Сохранение..." />
            )}

            <div className="space-y-2">
              <Label htmlFor="username" required>
                Имя пользователя
              </Label>
              <Input
                id="username"
                placeholder="Ваше имя"
                {...register('username')}
                disabled={isSubmitting}
              />
              {errors.username && (
                <p className="text-sm text-destructive">{errors.username.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" required>
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                {...register('email')}
                disabled={isSubmitting}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="flex items-center gap-3 pt-4">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Сохранение...' : 'Сохранить'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/')}
                disabled={isSubmitting}
              >
                Отмена
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="border-muted">
        <CardHeader>
          <CardTitle className="text-base">Информация профиля</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">ID:</span>
            <span className="font-mono">{user.id.substring(0, 12)}...</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Пользователь с:</span>
            <span>{new Date(user.created_at).toLocaleDateString('ru-RU')}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
