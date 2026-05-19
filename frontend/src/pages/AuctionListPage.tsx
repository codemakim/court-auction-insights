import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchAuctions, fetchSummary } from '../api'
import { AuctionCard } from '../components/AuctionCard'
import { Filters } from '../components/Filters'
import type { AuctionQuery } from '../types'

export function AuctionListPage() {
  const [query, setQuery] = useState<AuctionQuery>({ sort: 'latest' })
  const { data, isLoading, error } = useQuery({ queryKey: ['auctions', query], queryFn: () => fetchAuctions(query) })
  const { data: summary } = useQuery({ queryKey: ['auction-summary'], queryFn: fetchSummary })

  return (
    <main className="page">
      <header className="hero">
        <p>court auction insights</p>
        <h1>경매 인사이트</h1>
      </header>
      {summary ? (
        <section className="summary-strip">
          <div><strong>{summary.total_count.toLocaleString('ko-KR')}</strong><span>수집 물건</span></div>
          <div><strong>{(summary.sale_spec_status_counts.downloaded ?? 0).toLocaleString('ko-KR')}</strong><span>명세서 확보</span></div>
          <div><strong>{(summary.sale_spec_status_counts.download_pending ?? 0).toLocaleString('ko-KR')}</strong><span>명세서 대기</span></div>
          <div><strong>{summary.image_count.toLocaleString('ko-KR')}</strong><span>사진</span></div>
          <div><strong>{(summary.enrichment_status_counts.completed ?? 0).toLocaleString('ko-KR')}</strong><span>AI 요약</span></div>
        </section>
      ) : null}
      <Filters query={query} onChange={setQuery} districts={summary?.districts ?? []} subtypes={summary?.subtypes ?? []} />
      {isLoading ? <p>불러오는 중...</p> : null}
      {error ? <p>목록을 불러오지 못했습니다.</p> : null}
      {!isLoading && !error && !data?.length ? <p>표시할 물건이 없습니다.</p> : null}
      {data?.length ? <section className="grid">{data.map((auction) => <AuctionCard key={auction.id} auction={auction} />)}</section> : null}
    </main>
  )
}
