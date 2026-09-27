
import { useMemo, useState } from 'react'
import { Search, Users } from 'lucide-react'
import { useAuthStore } from '@/features/auth/store/authStore'
import { useUserDirectory } from '@/features/members/api/userDirectoryApi'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Avatar } from '@/shared/ui/avatar'
import { EmptyState } from '@/shared/ui/empty-state'
import { Input } from '@/shared/ui/input'
import { Button } from '@/shared/ui/button'
import { Skeleton } from '@/shared/ui/skeleton'
import { useDebounce } from '@/shared/hooks/useDebounce'

export function GlobalTeamPage() {
  const user = useAuthStore((state) => state.user)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebounce(search, 400)

  const { data, isLoading, error } = useUserDirectory({
    page,
    page_size: 20,
    search: debouncedSearch || undefined,
  })

  const users = useMemo(() => data?.items ?? [], [data])
  const totalPages = data?.total_pages ?? 0

  return (
    <div className="animate-rise space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
            Команда
          </p>
          <h1 className="mt-1.5">Глобальная команда</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Просмотрите всех участников системы
          </p>
        </div>
        <Badge variant="secondary" className="shrink-0">
          {data?.total ?? 0} участников
        </Badge>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Поиск по имени или email..."
          value={search}
          onChange={(event) => {
            setSearch(event.target.value)
            setPage(1)
          }}
          className="pl-9"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Участники команды</CardTitle>
          <CardDescription>Все зарегистрированные пользователи</CardDescription>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {isLoading ? (
            <div className="space-y-2.5">
              {[...Array(6)].map((_, index) => (
                <div key={index} className="flex items-center gap-3">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-48" />
                  </div>
                  <Skeleton className="h-6 w-20 rounded-md" />
                </div>
              ))}
            </div>
          ) : error ? (
            <EmptyState
              icon={<Users className="h-8 w-8" />}
              title="Не удалось загрузить участников"
              description="Проверьте подключение и попробуйте обновить страницу"
              className="py-8"
            />
          ) : users.length === 0 ? (
            <EmptyState
              icon={<Users className="h-8 w-8" />}
              title="Участники не найдены"
              description={
                debouncedSearch
                  ? 'Попробуйте изменить поисковый запрос'
                  : 'В системе пока нет зарегистрированных участников'
              }
              className="py-8"
            />
          ) : (
            <div className="divide-y divide-border/60">
              {users.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between gap-4 py-3 transition-colors hover:bg-secondary/30"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <Avatar className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-border/70 bg-primary/10 text-sm font-semibold text-primary">
                      {member.username.charAt(0).toUpperCase()}
                    </Avatar>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="truncate text-sm font-medium">{member.username}</p>
                        {user?.id === member.id && (
                          <Badge variant="outline" className="text-[0.6875rem]">
                            Вы
                          </Badge>
                        )}
                      </div>
                      <p className="truncate text-xs text-muted-foreground">
                        {member.email}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={member.is_active ? 'success' : 'secondary'}
                    className="shrink-0"
                  >
                    {member.is_active ? 'Активен' : 'Неактивен'}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((current) => Math.max(1, current - 1))}
            disabled={page === 1}
          >
            Назад
          </Button>
          <span className="text-xs text-muted-foreground">
            Страница {page} из {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
            disabled={page === totalPages}
          >
            Вперед
          </Button>
        </div>
      )}
    </div>
  )
}
