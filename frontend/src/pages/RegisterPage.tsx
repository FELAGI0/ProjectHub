
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Command } from 'lucide-react'
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
    <div className="auth-shell flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex items-center justify-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/12 text-primary">
            <Command className="h-4.5 w-4.5" />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-tight">ProjectHub</p>
            <p className="text-[0.6875rem] text-muted-foreground">Workspace</p>
          </div>
        </div>

        <Card className="glass-panel animate-in zoom-in-95">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl">Регистрация</CardTitle>
            <CardDescription>Создайте аккаунт, чтобы начать работу</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  Не удалось создать аккаунт. Попробуйте еще раз.
                </Alert>
              )}

              {isPending && <FormSubmitting message="Создание аккаунта..." />}

              <div className="space-y-1.5">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="user@example.com"
                  disabled={isPending}
                  autoComplete="email"
                  {...registerField('email')}
                />
                {errors.email && (
                  <p className="text-xs text-destructive">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="username">Имя пользователя</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="username"
                  disabled={isPending}
                  autoComplete="username"
                  {...registerField('username')}
                />
                {errors.username && (
                  <p className="text-xs text-destructive">{errors.username.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="password">Пароль</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Минимум 12 символов"
                  disabled={isPending}
                  autoComplete="new-password"
                  {...registerField('password')}
                />
                {errors.password && (
                  <p className="text-xs text-destructive">{errors.password.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={isPending}>
                {isPending ? 'Создание аккаунта...' : 'Зарегистрироваться'}
              </Button>

              <div className="text-center text-xs text-muted-foreground">
                Уже есть аккаунт?{' '}
                <Link to="/login" className="font-medium text-primary hover:underline">
                  Войти
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
