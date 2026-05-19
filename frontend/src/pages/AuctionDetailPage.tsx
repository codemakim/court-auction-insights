import { useQuery } from '@tanstack/react-query'
import { fetchAuctionDetail, mediaUrl } from '../api'

export function AuctionDetailPage({ auctionId }: { auctionId: number }) {
  const { data, isLoading, error } = useQuery({ queryKey: ['auction', auctionId], queryFn: () => fetchAuctionDetail(auctionId) })

  if (isLoading) return <main className="page"><p>불러오는 중...</p></main>
  if (error || !data) return <main className="page"><p>상세 정보를 불러오지 못했습니다.</p></main>

  const bullets = data.enrichment?.summary_bullets_json ? JSON.parse(data.enrichment.summary_bullets_json) as string[] : []
  const saleSpecLabel =
    data.sale_spec_status === 'not_uploaded'
      ? '명세서 미업로드'
      : data.sale_spec_status === 'download_pending'
        ? '명세서 다운로드 대기'
        : data.sale_spec_status === 'download_failed'
          ? '명세서 다운로드 실패'
          : data.sale_spec_status === 'extraction_failed'
            ? '명세서 추출 실패'
            : '명세서 있음'
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
            <span>{saleSpecLabel}</span>
          </div>
          <h1>{data.address}</h1>
          <dl className="detail-facts metrics">
            <div><dt>사건번호</dt><dd>{data.external_key}</dd></div>
            <div><dt>동</dt><dd>{data.neighborhood ?? '-'}</dd></div>
            <div><dt>건물명</dt><dd>{data.building_name ?? '-'}</dd></div>
            <div><dt>층/호</dt><dd>{[data.floor ? `${data.floor}층` : null, data.unit].filter(Boolean).join(' ') || '-'}</dd></div>
            <div><dt>전체층</dt><dd>{data.total_floors == null ? '-' : `${data.total_floors}층`}</dd></div>
            <div><dt>사용승인일</dt><dd>{data.approval_date ?? '-'}</dd></div>
            <div><dt>감정가</dt><dd>{data.appraisal_value?.toLocaleString('ko-KR') ?? '-'}원</dd></div>
            <div><dt>최저가</dt><dd>{data.minimum_sale_price?.toLocaleString('ko-KR') ?? '-'}원</dd></div>
            <div><dt>할인율</dt><dd>{data.discount_rate == null ? '-' : `${data.discount_rate}%`}</dd></div>
            <div><dt>감정가 대비 차액</dt><dd>{data.price_gap == null ? '-' : `${data.price_gap.toLocaleString('ko-KR')}원`}</dd></div>
            <div><dt>유찰</dt><dd>{data.failed_auction_count == null ? '-' : `${data.failed_auction_count}회`}</dd></div>
            <div><dt>매각기일</dt><dd>{data.sale_date ?? '-'}</dd></div>
            <div><dt>상태</dt><dd>{data.current_status ?? '-'}</dd></div>
          </dl>
          {data.area_note ? (
            <div className="area-note">
              <strong>면적 참고</strong>
              <p>{data.area_note}</p>
            </div>
          ) : null}
        </div>
      </section>
      <section className="info-panel">
        <h2>매각물건명세서</h2>
        <p>{saleSpecLabel}</p>
        {data.sale_spec_error ? <p className="muted">최근 오류: {data.sale_spec_error}</p> : null}
        {data.sale_spec_markdown ? <pre>{data.sale_spec_markdown}</pre> : null}
      </section>
      <section className="info-panel">
        <h2>감정평가 요약</h2>
        {data.appraisal_summary ? <pre>{data.appraisal_summary}</pre> : <p>수집된 감정평가 요약이 없습니다.</p>}
      </section>
      <section className="ai-panel">
        <h2>AI 요약</h2>
        {data.enrichment_status === 'pending' ? (
          <p>AI 요약 전입니다. 매각물건명세서가 준비되면 순차적으로 요약됩니다.</p>
        ) : data.enrichment_status === 'failed' ? (
          <p className="risk">AI 요약 실패: {data.enrichment_error ?? '오류 기록 없음'}</p>
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
