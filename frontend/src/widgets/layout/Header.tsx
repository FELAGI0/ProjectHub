
import { Menu, Moon, Sun, LogOut } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { useTheme } from '@/app/providers/ThemeProvider'
import { useLogout } from '@/features/auth/hooks/useAuth'
import { useAuthStore } from '@/features/auth/store/authStore'

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { theme, setTheme } = useTheme()
  const { mutate: logout } = useLogout()
  const user = useAuthStore((state) => state.user)

  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }

  const handleLogout = () => {
    logout()
  }

  return (
    <header className="sticky top-0 z-sticky flex h-16 items-center gap-3 border-b border-border/70 bg-background/80 px-4 backdrop-blur-xl supports-[backdrop-filter]:bg-background/65 sm:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
        aria-label="Открыть меню"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <div className="hidden flex-1 items-center gap-2 text-sm text-muted-foreground md:flex">
        <span className="font-medium text-foreground">ProjectHub</span>
        <span className="text-muted-foreground/50">/</span>
        <span>Workspace</span>
      </div>
      <div className="flex-1 md:hidden" />

      {user && (
        <div className="hidden items-center gap-2.5 sm:flex">
          <span className="flex h-8 w-8 items-center justify-center rounded-full border border-border/70 bg-secondary/70 text-xs font-semibold text-foreground">
            {user.username.charAt(0).toUpperCase()}
          </span>
          <span className="text-sm font-medium text-foreground">{user.username}</span>
        </div>
      )}

      <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Переключить тему">
        {theme === 'dark' ? (
          <Moon className="h-5 w-5" />
        ) : (
          <Sun className="h-5 w-5" />
        )}
      </Button>

      <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Выйти">
        <LogOut className="h-5 w-5" />
      </Button>
    </header>
  )
}
