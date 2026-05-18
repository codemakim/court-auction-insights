import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'
import { AuctionDetailPage } from './pages/AuctionDetailPage'
import { AuctionListPage } from './pages/AuctionListPage'

const queryClient = new QueryClient()

function CurrentPage() {
  const detailMatch = window.location.pathname.match(/^\/auctions\/(\d+)$/)
  if (detailMatch) return <AuctionDetailPage auctionId={Number(detailMatch[1])} />
  return <AuctionListPage />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <CurrentPage />
    </QueryClientProvider>
  )
}
