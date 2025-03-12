import * as React from 'react'
import { Outlet, createRootRoute } from '@tanstack/react-router'
import Aurora from '../components/background/Aurora'

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  return (
    <React.Fragment>
      <Aurora
        colorStops={["#3A29FF", "#FF94B4", "#FF3232"]}
        blend={0.5}
        amplitude={1.0}
        speed={0.5}
        />
      <div>Hello "__root"!</div>
      <img src="/logo.svg" alt="Bingo" className="h-32" />
      <Outlet />
    </React.Fragment>
  )
}
