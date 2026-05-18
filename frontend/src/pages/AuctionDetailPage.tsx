import { useQuery } from '@tanstack/react-query'
import { fetchAuctionDetail, mediaUrl } from '../api'

export function AuctionDetailPage({ auctionId }: { auctionId: number }) {
  const { data, isLoading, error } = useQuery({ queryKey: ['auction', auctionId], queryFn: () => fetchAuctionDetail(auctionId) })

  if (isLoading) return <main className="page"><p>불러오는 중...</p></main>
  if (error || !data) return <main className="page"><p>상세 정보를 불러오지 못했습니다.</p></main>

  const bullets = data.enrichment?.summary_bullets_json ? JSON.parse(data.enrichment.summary_bullets_json) as string[] : []

  return (
    <main className="page detail-page">
      <a className="back-link" href="/">← 목록으로</a>
      <section className="detail-hero">
        <div className="gallery">
          {data.images.length ? data.images.map((image) => (
            <img key={image.image_index} src={mediaUrl(image.url)} alt={image.alt_text ?? data.address} />
          )) : <div className="cover empty">등록된 사진 없음</div>}
        </div>
        <div>
          <div className="badges">
            {data.district ? <span>{data.district}</span> : null}
            {data.residential_subtype ? <span>{data.residential_subtype}</span> : null}
            {data.sale_spec_status === 'not_uploaded' ? <span>명세서 미업로드</span> : <span>명세서 있음</span>}
          </div>
          <h1>{data.address}</h1>
          <dl className="detail-facts">
            <div><dt>사건번호</dt><dd>{data.external_key}</dd></div>
            <div><dt>최저가</dt><dd>{data.minimum_sale_price?.toLocaleString('ko-KR') ?? '-'}원</dd></div>
            <div><dt>매각기일</dt><dd>{data.sale_date ?? '-'}</dd></div>
            <div><dt>상태</dt><dd>{data.current_status ?? '-'}</dd></div>
          </dl>
        </div>
      </section>
      <section className="ai-panel">
        <h2>AI 요약</h2>
        {data.enrichment_status === 'pending' ? (
          <p>AI 요약 전입니다. 매각물건명세서가 준비되면 순차적으로 요약됩니다.</p>
        ) : (
          <>
            <h3>{data.enrichment?.summary_title}</h3>
            <ul>{bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}</ul>
            {data.enrichment?.risk_comment ? <p className="risk">{data.enrichment.risk_comment}</p> : null}
          </>
        )}
      </section>
    </main>
  )
}
