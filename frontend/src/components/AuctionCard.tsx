import { mediaUrl } from '../api'
import type { Auction } from '../types'

type Props = { auction: Auction }

function saleSpecLabel(status: Auction['sale_spec_status']) {
  if (status === 'not_uploaded') return '명세서 미업로드'
  if (status === 'download_pending') return '명세서 다운로드 대기'
  if (status === 'download_failed') return '명세서 다운로드 실패'
  if (status === 'extraction_failed') return '명세서 추출 실패'
  return '명세서 있음'
}

export function AuctionCard({ auction }: Props) {
  return (
    <a className="card" href={`/auctions/${auction.id}`}>
      {auction.images[0] ? (
        <img className="cover" src={mediaUrl(auction.images[0].url)} alt={auction.images[0].alt_text ?? auction.address} />
      ) : (
        <div className="cover empty">등록된 사진 없음</div>
      )}
      <div className="body">
        <div className="badges">
          {auction.district ? <span>{auction.district}</span> : null}
          {auction.residential_subtype ? <span>{auction.residential_subtype}</span> : null}
          <span>{saleSpecLabel(auction.sale_spec_status)}</span>
          <span>{auction.enrichment_status === 'pending' ? 'AI 요약 전' : 'AI 요약 완료'}</span>
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
          <div>
            <dt>유찰</dt>
            <dd>{auction.failed_auction_count == null ? '-' : `${auction.failed_auction_count}회`}</dd>
          </div>
        </dl>
      </div>
    </a>
  )
}
