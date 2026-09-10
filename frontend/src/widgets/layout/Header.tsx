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
    <header className="sticky top-0 z-sticky flex h-16 items-center gap-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-6">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
        aria-label="Открыть меню"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <div className="flex-1" />

      {user && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">{user.username}</span>
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
