import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, Folder } from 'lucide-react'
import { useProjects } from '@/features/projects/hooks/useProjects'
import { useDebounce } from '@/shared/hooks/useDebounce'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { ProjectCardSkeleton } from '@/shared/ui/skeleton'
import { EmptyState } from '@/shared/ui/empty-state'
import type { Project } from '@/features/projects/types'

export function ProjectsListPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebounce(search, 500)

  const { data, isLoading, error } = useProjects({
    page,
    page_size: 20,
    search: debouncedSearch || undefined,
  })

  const projects = data?.items || []
  const totalPages = data ? Math.ceil(data.total / 20) : 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Проекты</h1>
          <p className="text-muted-foreground mt-1">
            Управляйте проектами и задачами
          </p>
        </div>
        <Button onClick={() => navigate('/projects/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Создать проект
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Поиск проектов..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="pl-9"
          />
        </div>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">
              Не удалось загрузить проекты. Попробуйте еще раз.
            </p>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <ProjectCardSkeleton key={i} />
          ))}
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          icon={<Folder className="h-12 w-12" />}
          title={search ? 'Проекты не найдены' : 'Пока нет проектов'}
          description={
            search
              ? 'Попробуйте изменить поисковый запрос'
              : 'Создайте первый проект, чтобы начать работу'
          }
          action={
            !search && (
              <Button onClick={() => navigate('/projects/new')}>
                <Plus className="mr-2 h-4 w-4" />
                Создать проект
              </Button>
            )
          }
        />
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((project: Project) => (
              <Card
                key={project.id}
                className="hover:shadow-lg hover:scale-[1.02] transition-all duration-200 cursor-pointer"
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded bg-primary/10">
                        <Folder className="h-5 w-5 text-primary" />
                      </div>
                      <div className="min-w-0">
                        <CardTitle className="text-base truncate">
                          {project.name}
                        </CardTitle>
                      </div>
                    </div>
                    {project.is_active && (
                      <Badge variant="secondary" className="shrink-0">
                        Активный
                      </Badge>
                    )}
                  </div>
                  <CardDescription className="line-clamp-2 mt-2">
                    {project.description || 'Без описания'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">
                    Обновлен {new Date(project.updated_at).toLocaleDateString('ru-RU')}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Назад
              </Button>
              <span className="text-sm text-muted-foreground">
                Страница {page} из {totalPages}
              </span>
              <Button
                variant="outline"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Вперед
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
