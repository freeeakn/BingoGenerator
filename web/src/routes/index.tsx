import { createFileRoute } from '@tanstack/react-router'
import { BingoGenerator } from '../components/BingoGenerator'

export const Route = createFileRoute('/')({
  component: BingoGenerator,
})
