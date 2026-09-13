import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, UserPlus, Shield, Edit2, Trash2, Crown } from 'lucide-react'
import { useProjectMembers, useRemoveMember } from '@/features/project-members/hooks/useProjectMembers'
import { useProject } from '@/features/projects/hooks/useProjects'
import { useAuthStore } from '@/features/auth/store/authStore'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Avatar } from '@/shared/ui/avatar'
import { Skeleton } from '@/shared/ui/skeleton'
import { EmptyState } from '@/shared/ui/empty-state'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogFooter,
} from '@/shared/ui/dialog'
import { cn } from '@/shared/utils/cn'
import { PROJECT_ROLE_LABELS, PROJECT_ROLE_COLORS } from '@/shared/constants/project'

export function TeamPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const [memberToRemove, setMemberToRemove] = useState<{ id: string; name: string } | null>(null)

  const { data: projectData } = useProject(projectId || '')
  const { data, isLoading, error } = useProjectMembers(projectId || '', { page_size: 100 })
  const { mutate: removeMember, isPending: isRemoving } = useRemoveMember()

  const members = data?.items || []
  const currentUserMember = members.find((m) => m.user_id === user?.id)
  const canManageMembers = currentUserMember && ['ADMIN', 'OWNER'].includes(currentUserMember.role)

  const handleRemove = () => {
    if (!memberToRemove || !projectId) return

    removeMember(
      { projectId, userId: memberToRemove.id },
      {
        onSuccess: () => {
          setMemberToRemove(null)
        },
      }
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}`)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К проекту
        </Button>
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">
              Не удалось загрузить участников команды. Попробуйте еще раз.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate(`/projects/${projectId}`)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          К проекту
        </Button>
        {canManageMembers && (
          <Button onClick={() => navigate(`/projects/${projectId}/team/add`)}>
            <UserPlus className="mr-2 h-4 w-4" />
            Добавить участника
          </Button>
        )}
      </div>

      <div>
        <h1 className="text-3xl font-bold">Команда</h1>
        <p className="text-muted-foreground mt-1">
          Участники проекта {projectData?.name}
        </p>
      </div>

      {members.length === 0 ? (
        <EmptyState
          icon={<Shield className="h-12 w-12" />}
          title="Нет участников"
          description="Добавьте участников для совместной работы над проектом"
        />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Участники ({members.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {members.map((member) => {
                const isOwner = member.role === 'OWNER'
                const isCurrentUser = member.user_id === user?.id
                const canRemove = canManageMembers && !isOwner && !isCurrentUser

                return (
                  <div
                    key={member.id}
                    className="flex items-center justify-between gap-4 p-4 rounded-lg border border-border"
                  >
                    <div className="flex items-center gap-3">
                      <Avatar className="h-10 w-10 flex items-center justify-center bg-primary/10 text-primary">
                        {member.user.username.charAt(0).toUpperCase()}
                      </Avatar>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{member.user.username}</p>
                          {isOwner && <Crown className="h-4 w-4 text-yellow-500" />}
                          {isCurrentUser && (
                            <Badge variant="outline" className="text-xs">
                              Вы
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {member.user.email}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Badge
                        variant="secondary"
                        className={cn(PROJECT_ROLE_COLORS[member.role])}
                      >
                        {PROJECT_ROLE_LABELS[member.role]}
                      </Badge>
                      {canRemove && (
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() =>
                              navigate(`/projects/${projectId}/team/members/${member.user_id}/edit`)
                            }
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() =>
                              setMemberToRemove({
                                id: member.user_id,
                                name: member.user.username,
                              })
                            }
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      <Dialog
        open={!!memberToRemove}
        onOpenChange={(open) => !open && setMemberToRemove(null)}
      >
        <DialogContent>
          <DialogHeader onClose={() => setMemberToRemove(null)}>
            <DialogTitle>Удаление участника</DialogTitle>
            <DialogDescription>
              Вы уверены, что хотите удалить этого участника?
            </DialogDescription>
          </DialogHeader>
          <DialogBody>
            <p className="text-sm">
              Пользователь <strong>{memberToRemove?.name}</strong> будет удален из проекта и потеряет доступ ко всем ресурсам.
            </p>
          </DialogBody>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setMemberToRemove(null)}
              disabled={isRemoving}
            >
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={handleRemove}
              disabled={isRemoving}
            >
              {isRemoving ? 'Удаление...' : 'Удалить участника'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
