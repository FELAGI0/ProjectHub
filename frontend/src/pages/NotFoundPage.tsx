import { useNavigate } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'

export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-muted">
              <span className="text-5xl font-bold text-muted-foreground">404</span>
            </div>
          </div>
          <CardTitle>Страница не найдена</CardTitle>
          <CardDescription>
            Запрашиваемая страница не существует или была перемещена.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <Button onClick={() => navigate('/')} variant="default" className="w-full">
            <Home className="mr-2 h-4 w-4" />
            На главную
          </Button>
          <Button onClick={() => navigate(-1)} variant="outline" className="w-full">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
