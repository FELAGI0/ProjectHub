
import { useNavigate } from 'react-router-dom'
import { Plus, Folder, CheckSquare } from 'lucide-react'
import { useAuthStore } from '@/features/auth/store/authStore'
import { useProjects } from '@/features/projects/hooks/useProjects'
import { useTotalTasksCount } from '@/features/tasks/hooks/useTasks'
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
  const { data: tasksCount, isLoading: isLoadingTasksCount } = useTotalTasksCount()

  const projects = projectsData?.items || []

  const metrics = [
    {
      label: 'Всего проектов',
      value: projectsData?.total || 0,
      icon: Folder,
      loading: isLoadingProjects,
    },
    {
      label: 'Активных проектов',
      value: projects.filter((p: Project) => p.is_active).length,
      icon: Folder,
      loading: isLoadingProjects,
    },
    {
      label: 'Всего задач',
      value: tasksCount || 0,
      icon: CheckSquare,
      loading: isLoadingTasksCount,
    },
  ]

  return (
    <div className="animate-rise space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
            Обзор
          </p>
          <h1 className="mt-1.5">Панель управления</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Добро пожаловать, {user?.username || 'Пользователь'}
          </p>
        </div>
        <Button onClick={() => navigate('/projects/new')}>
          <Plus className="h-4 w-4" />
          Создать проект
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {metrics.map((metric) => (
          <Card
            key={metric.label}
            className="group relative overflow-hidden hover:border-border hover:shadow-md"
          >
            <div className="pointer-events-none absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {metric.label}
              </CardTitle>
              <metric.icon className="h-4 w-4 text-muted-foreground transition-colors group-hover:text-primary" />
            </CardHeader>
            <CardContent>
              {metric.loading ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-3xl font-semibold tracking-tight tabular-nums">
                  {metric.value}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.5fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Последние проекты</CardTitle>
            <CardDescription>Ваши недавно обновленные проекты</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProjects ? (
              <div className="space-y-2.5">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <Skeleton className="h-10 w-10 rounded-xl" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                  </div>
                ))}
              </div>
            ) : projects.length === 0 ? (
              <EmptyState
                icon={<Folder className="h-7 w-7" />}
                title="Пока нет проектов"
                description="Создайте первый проект, чтобы начать работу"
              />
            ) : (
              <div className="space-y-1.5">
                {projects.slice(0, 5).map((project: Project) => (
                  <div
                    key={project.id}
                    className="group flex items-center justify-between gap-3 rounded-lg border border-transparent p-3 transition-colors hover:border-border/80 hover:bg-secondary/50"
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-primary/15 bg-primary/10 transition-colors group-hover:bg-primary/15">
                        <Folder className="h-4.5 w-4.5 text-primary" />
                      </div>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">{project.name}</p>
                        <p className="truncate text-xs text-muted-foreground">
                          {project.description || 'Без описания'}
                        </p>
                      </div>
                    </div>
                    {project.is_active ? (
                      <Badge variant="success" className="shrink-0">
                        Активный
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="shrink-0">
                        Архив
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
          <CardContent className="space-y-2.5">
            <Button
              className="w-full justify-start"
              variant="outline"
              onClick={() => navigate('/projects/new')}
            >
              <Plus className="h-4 w-4" />
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
              <Plus className="h-4 w-4" />
              Создать задачу
            </Button>
            <div className="mt-4 rounded-lg border border-dashed border-border/80 p-4">
              <p className="text-sm font-medium">Минимализм и фокус</p>
              <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                Только важные метрики, проекты и задачи — без лишнего визуального шума.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
