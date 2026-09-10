import { useNavigate } from 'react-router-dom'
import { Plus, Folder, CheckSquare } from 'lucide-react'
import { useAuthStore } from '@/features/auth/store/authStore'
import { useProjects } from '@/features/projects/hooks/useProjects'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Skeleton } from '@/shared/ui/skeleton'
import { EmptyState } from '@/shared/ui/empty-state'
import type { Project } from '@/features/projects/types'

export function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const navigate = useNavigate()
  const { data: projectsData, isLoading: isLoadingProjects } = useProjects({
    page: 1,
    page_size: 5,
  })

  const projects = projectsData?.items || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Панель управления</h1>
        <p className="text-muted-foreground">
          Добро пожаловать, {user?.username || 'Пользователь'}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего проектов</CardTitle>
            <Folder className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoadingProjects ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{projectsData?.total || 0}</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активных проектов</CardTitle>
            <Folder className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoadingProjects ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">
                {projects.filter((p: Project) => p.is_active).length}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего задач</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Последние проекты</CardTitle>
            <CardDescription>Ваши недавно обновленные проекты</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProjects ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <Skeleton className="h-10 w-10 rounded" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                  </div>
                ))}
              </div>
            ) : projects.length === 0 ? (
              <EmptyState
                icon={<Folder className="h-8 w-8" />}
                title="Пока нет проектов"
                description="Создайте первый проект, чтобы начать работу"
              />
            ) : (
              <div className="space-y-3">
                {projects.slice(0, 5).map((project: Project) => (
                  <div
                    key={project.id}
                    className="flex items-center justify-between gap-3 p-3 rounded-lg border border-border hover:bg-accent cursor-pointer transition-colors"
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded bg-primary/10">
                        <Folder className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{project.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {project.description || 'Без описания'}
                        </p>
                      </div>
                    </div>
                    {project.is_active && (
                      <Badge variant="secondary" className="shrink-0">
                        Активный
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Быстрые действия</CardTitle>
            <CardDescription>Часто используемые операции</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              className="w-full justify-start"
              variant="outline"
              onClick={() => navigate('/projects/new')}
            >
              <Plus className="mr-2 h-4 w-4" />
              Создать проект
            </Button>
            <Button
              className="w-full justify-start"
              variant="outline"
              disabled={projects.length === 0}
              onClick={() => {
                if (projects[0]) {
                  navigate(`/projects/${projects[0].id}/tasks/new`)
                }
              }}
            >
              <Plus className="mr-2 h-4 w-4" />
              Создать задачу
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
