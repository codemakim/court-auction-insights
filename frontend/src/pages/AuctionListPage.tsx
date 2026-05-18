import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchAuctions } from '../api'
import { AuctionCard } from '../components/AuctionCard'
import { Filters } from '../components/Filters'
import type { AuctionQuery } from '../types'

export function AuctionListPage() {
  const [query, setQuery] = useState<AuctionQuery>({ sort: 'latest' })
  const { data, isLoading, error } = useQuery({ queryKey: ['auctions', query], queryFn: () => fetchAuctions(query) })

  return (
    <main className="page">
      <header className="hero">
        <p>court auction insights</p>
        <h1>경매 인사이트</h1>
      </header>
      <Filters query={query} onChange={setQuery} />
      {isLoading ? <p>불러오는 중...</p> : null}
      {error ? <p>목록을 불러오지 못했습니다.</p> : null}
      {!isLoading && !error && !data?.length ? <p>표시할 물건이 없습니다.</p> : null}
      {data?.length ? <section className="grid">{data.map((auction) => <AuctionCard key={auction.id} auction={auction} />)}</section> : null}
    </main>
  )
}
