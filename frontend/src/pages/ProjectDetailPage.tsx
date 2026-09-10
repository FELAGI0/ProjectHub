import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Calendar, User, Settings, LayoutGrid, Users } from 'lucide-react'
import { useProject } from '@/features/projects/hooks/useProjects'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const { data: project, isLoading, error } = useProject(projectId || '')

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" disabled>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К проектам
        </Button>
        <div className="flex items-center gap-4 mb-6">
          <div className="h-16 w-16 rounded-lg bg-muted animate-pulse" />
          <div className="space-y-2 flex-1">
            <div className="h-8 w-48 bg-muted animate-pulse rounded" />
            <div className="h-4 w-32 bg-muted animate-pulse rounded" />
          </div>
        </div>
        <Card>
          <CardHeader>
            <div className="h-6 w-32 bg-muted animate-pulse rounded" />
            <div className="h-4 w-full bg-muted animate-pulse rounded mt-2" />
          </CardHeader>
        </Card>
        <div className="grid gap-4 md:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <div className="h-4 w-24 bg-muted animate-pulse rounded" />
              </CardHeader>
              <CardContent>
                <div className="h-6 w-32 bg-muted animate-pulse rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="space-y-6">
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate('/projects')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К проектам
        </Button>
        <Button
          variant="outline"
          onClick={() => navigate(`/projects/${projectId}/settings`)}
        >
          <Settings className="mr-2 h-4 w-4" />
          Настройки
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-primary/10">
          <span className="text-2xl font-bold text-primary">
            {project.name.charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{project.name}</h1>
            {project.is_active && (
              <Badge variant="secondary">Активный</Badge>
            )}
          </div>
          <p className="text-muted-foreground mt-1">
            {project.description || 'Без описания'}
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Создан</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              {new Date(project.created_at).toLocaleDateString('ru-RU')}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Обновлен</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              {new Date(project.updated_at).toLocaleDateString('ru-RU')}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Владелец</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              {project.owner_id.substring(0, 8)}...
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Быстрые действия</CardTitle>
          <CardDescription>
            Часто используемые операции для этого проекта
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button
            className="w-full justify-start"
            variant="outline"
            onClick={() => navigate(`/projects/${projectId}/kanban`)}
          >
            <LayoutGrid className="mr-2 h-4 w-4" />
            Открыть Kanban-доску
          </Button>
          <Button
            className="w-full justify-start"
            variant="outline"
            onClick={() => navigate(`/projects/${projectId}/tasks/new`)}
          >
            <Calendar className="mr-2 h-4 w-4" />
            Создать задачу
          </Button>
          <Button
            className="w-full justify-start"
            variant="outline"
            onClick={() => navigate(`/projects/${projectId}/team`)}
          >
            <Users className="mr-2 h-4 w-4" />
            Управление командой
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
