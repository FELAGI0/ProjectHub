
import { Home, FolderKanban, Users, Settings, Command } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { cn } from '@/shared/utils/cn'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const navigation = [
  { name: 'Панель', href: '/', icon: Home, shortcut: 'D' },
  { name: 'Проекты', href: '/projects', icon: FolderKanban, shortcut: 'P' },
  { name: 'Команда', href: '/team', icon: Users, shortcut: 'T' },
  { name: 'Настройки', href: '/settings', icon: Settings, shortcut: 'S' },
]

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-overlay bg-background/70 backdrop-blur-md lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-0 z-modal h-full w-64 border-r border-sidebar-border/90 bg-sidebar/95 backdrop-blur-xl transition-transform duration-300 ease-out lg:sticky lg:top-0 lg:z-auto lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-16 items-center gap-2.5 border-b border-sidebar-border/80 px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/12 text-primary">
            <Command className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold tracking-tight text-sidebar-foreground">
              ProjectHub
            </p>
            <p className="truncate text-[0.6875rem] text-muted-foreground">
              Workspace
            </p>
          </div>
        </div>

        <nav className="flex flex-col gap-1 p-3">
          <p className="px-3 pb-1 pt-2 text-[0.6875rem] font-medium uppercase tracking-[0.12em] text-muted-foreground/70">
            Навигация
          </p>
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={() => onClose()}
              className={({ isActive }) =>
                cn(
                  'group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-200',
                  isActive
                    ? 'bg-primary/12 text-primary'
                    : 'text-sidebar-foreground/75 hover:bg-secondary/70 hover:text-sidebar-foreground'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon
                    className={cn(
                      'h-4.5 w-4.5 shrink-0 transition-colors',
                      isActive
                        ? 'text-primary'
                        : 'text-muted-foreground group-hover:text-sidebar-foreground'
                    )}
                  />
                  <span className="flex-1">{item.name}</span>
                  <span className="rounded border border-sidebar-border/80 px-1.5 py-0.5 font-mono text-[0.625rem] text-muted-foreground/70 opacity-0 transition-opacity group-hover:opacity-100">
                    {item.shortcut}
                  </span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-4 left-3 right-3 rounded-lg border border-sidebar-border/70 bg-secondary/40 p-3">
          <p className="text-xs font-medium text-sidebar-foreground">ProjectHub</p>
          <p className="mt-1 text-[0.6875rem] leading-relaxed text-muted-foreground">
            Минималистичное рабочее пространство
          </p>
        </div>
      </aside>
    </>
  )
}
