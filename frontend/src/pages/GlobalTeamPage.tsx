import { useState } from 'react'
import { Users } from 'lucide-react'
import { useAuthStore } from '@/features/auth/store/authStore'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Avatar } from '@/shared/ui/avatar'
import { EmptyState } from '@/shared/ui/empty-state'

export function GlobalTeamPage() {
  const user = useAuthStore((state) => state.user)
  const [teamMembers] = useState<any[]>([])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Глобальная команда</h1>
          <p className="text-muted-foreground mt-1">
            Просмотрите всех участников системы
          </p>
        </div>
      </div>

      {teamMembers.length === 0 ? (
        <EmptyState
          icon={<Users className="h-12 w-12" />}
          title="Функция в разработке"
          description="Глобальная команда будет доступна в следующих обновлениях"
        />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Участники команды ({teamMembers.length})</CardTitle>
            <CardDescription>
              Все участники системы
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {teamMembers.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between gap-4 p-4 rounded-lg border border-border"
                >
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10 flex items-center justify-center bg-primary/10 text-primary">
                      {member.username.charAt(0).toUpperCase()}
                    </Avatar>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{member.username}</p>
                        {user?.id === member.id && (
                          <Badge variant="outline" className="text-xs">
                            Вы
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {member.email}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
