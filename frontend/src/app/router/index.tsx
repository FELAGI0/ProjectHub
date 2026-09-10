import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/widgets/layout'
import { DashboardPage } from '@/pages/DashboardPage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { ProjectsListPage } from '@/pages/ProjectsListPage'
import { ProjectCreatePage } from '@/pages/ProjectCreatePage'
import { ProjectDetailPage } from '@/pages/ProjectDetailPage'
import { ProjectSettingsPage } from '@/pages/ProjectSettingsPage'
import { KanbanPage } from '@/pages/KanbanPage'
import { TaskCreatePage } from '@/pages/TaskCreatePage'
import { TaskDetailPage } from '@/pages/TaskDetailPage'
import { TaskEditPage } from '@/pages/TaskEditPage'
import { TeamPage } from '@/pages/TeamPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { ProtectedRoute } from './ProtectedRoute'
import { PublicRoute } from './PublicRoute'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: '/register',
    element: (
      <PublicRoute>
        <RegisterPage />
      </PublicRoute>
    ),
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'projects',
        element: <ProjectsListPage />,
      },
      {
        path: 'projects/new',
        element: <ProjectCreatePage />,
      },
      {
        path: 'projects/:projectId',
        element: <ProjectDetailPage />,
      },
      {
        path: 'projects/:projectId/settings',
        element: <ProjectSettingsPage />,
      },
      {
        path: 'projects/:projectId/kanban',
        element: <KanbanPage />,
      },
      {
        path: 'projects/:projectId/tasks/new',
        element: <TaskCreatePage />,
      },
      {
        path: 'projects/:projectId/tasks/:taskId',
        element: <TaskDetailPage />,
      },
      {
        path: 'projects/:projectId/tasks/:taskId/edit',
        element: <TaskEditPage />,
      },
      {
        path: 'projects/:projectId/team',
        element: <TeamPage />,
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
])
