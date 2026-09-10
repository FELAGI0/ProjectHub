import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate, Link } from 'react-router-dom'
import { useRegister } from '@/features/auth/hooks/useAuth'
import { registerSchema, type RegisterFormData } from '@/features/auth/schemas'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert } from '@/shared/ui/alert'
import { FormSubmitting } from '@/shared/ui/form-submitting'

export function RegisterPage() {
  const navigate = useNavigate()
  const { mutate: register, isPending, error } = useRegister()

  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = (data: RegisterFormData) => {
    register(data, {
      onSuccess: () => {
        setTimeout(() => {
          navigate('/')
        }, 1000)
      },
    })
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Регистрация</CardTitle>
          <CardDescription>Создайте аккаунт, чтобы начать работу</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                Не удалось создать аккаунт. Попробуйте еще раз.
              </Alert>
            )}

            {isPending && (
              <FormSubmitting message="Создание аккаунта..." />
            )}

            <div className="space-y-2">
              <Label htmlFor="email">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="user@example.com"
                disabled={isPending}
                {...registerField('email')}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="username">
                Имя пользователя
              </Label>
              <Input
                id="username"
                type="text"
                placeholder="username"
                disabled={isPending}
                {...registerField('username')}
              />
              {errors.username && (
                <p className="text-sm text-destructive">{errors.username.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">
                Пароль
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="Минимум 12 символов"
                disabled={isPending}
                {...registerField('password')}
              />
              {errors.password && (
                <p className="text-sm text-destructive">{errors.password.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? 'Создание аккаунта...' : 'Зарегистрироваться'}
            </Button>

            <div className="text-center text-sm">
              Уже есть аккаунт?{' '}
              <Link to="/login" className="text-primary hover:underline">
                Войти
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
