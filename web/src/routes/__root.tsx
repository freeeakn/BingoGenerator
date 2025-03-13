import { createRootRoute, Outlet } from '@tanstack/react-router'
import { Layout } from '../components/layout/Layout'
import { ProtectedRoute } from '../components/ProtectedRoute'

export const Route = createRootRoute({
  component: () => (
    <Layout>
      <ProtectedRoute>
        <Outlet />
      </ProtectedRoute>
    </Layout>
  ),
})
