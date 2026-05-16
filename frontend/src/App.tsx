import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import './App.css'

type AuctionImage = {
  image_index: number
  alt_text: string | null
  url: string
}

type Auction = {
  id: number
  address: string
  minimum_sale_price: number | null
  sale_date: string | null
  current_status: string | null
  sale_spec_status: string
  images: AuctionImage[]
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const queryClient = new QueryClient()

async function fetchAuctions(): Promise<Auction[]> {
  const response = await fetch(`${API_BASE_URL}/api/auctions`)
  if (!response.ok) throw new Error('failed to load auctions')
  return response.json()
}

function AuctionList() {
  const { data, isLoading, error } = useQuery({ queryKey: ['auctions'], queryFn: fetchAuctions })

  if (isLoading) return <p>불러오는 중...</p>
  if (error) return <p>목록을 불러오지 못했습니다.</p>
  if (!data?.length) return <p>표시할 물건이 없습니다.</p>

  return (
    <main className="page">
      <header className="hero">
        <p>court auction insights</p>
        <h1>경매 인사이트</h1>
      </header>
      <section className="grid">
        {data.map((auction) => (
          <article className="card" key={auction.id}>
            {auction.images[0] ? (
              <img
                className="cover"
                src={`${API_BASE_URL}${auction.images[0].url}`}
                alt={auction.images[0].alt_text ?? auction.address}
              />
            ) : (
              <div className="cover empty">등록된 사진 없음</div>
            )}
            <div className="body">
              <div className="badges">
                {auction.sale_spec_status === 'not_uploaded' && <span>명세서 미업로드</span>}
                {auction.current_status && <span>{auction.current_status}</span>}
              </div>
              <h2>{auction.address}</h2>
              <dl className="facts">
                <div>
                  <dt>최저가</dt>
                  <dd>{auction.minimum_sale_price?.toLocaleString('ko-KR') ?? '-'}원</dd>
                </div>
                <div>
                  <dt>매각기일</dt>
                  <dd>{auction.sale_date ?? '-'}</dd>
                </div>
              </dl>
            </div>
          </article>
        ))}
      </section>
    </main>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuctionList />
    </QueryClientProvider>
  )
}
