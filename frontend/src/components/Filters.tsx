import type { AuctionQuery } from '../types'

type Props = {
  query: AuctionQuery
  onChange: (next: AuctionQuery) => void
  districts: string[]
  subtypes: string[]
}

export function Filters({ query, onChange, districts, subtypes }: Props) {
  const update = (key: keyof AuctionQuery, value: string) => onChange({ ...query, [key]: value })

  return (
    <section className="filters">
      <input placeholder="주소·사건번호 검색" value={query.q ?? ''} onChange={(event) => update('q', event.target.value)} />
      <select value={query.district ?? ''} onChange={(event) => update('district', event.target.value)}>
        <option value="">전체 구</option>
        {districts.map((district) => <option key={district} value={district}>{district}</option>)}
      </select>
      <select value={query.subtype ?? ''} onChange={(event) => update('subtype', event.target.value)}>
        <option value="">전체 유형</option>
        {subtypes.map((subtype) => <option key={subtype} value={subtype}>{subtype}</option>)}
      </select>
      <input inputMode="numeric" placeholder="최저가 이상" value={query.min_price ?? ''} onChange={(event) => update('min_price', event.target.value)} />
      <input inputMode="numeric" placeholder="최저가 이하" value={query.max_price ?? ''} onChange={(event) => update('max_price', event.target.value)} />
      <select value={query.sale_spec_status ?? ''} onChange={(event) => update('sale_spec_status', event.target.value)}>
        <option value="">명세서 전체</option>
        <option value="downloaded">명세서 있음</option>
        <option value="not_uploaded">미업로드</option>
        <option value="download_pending">다운로드 대기</option>
        <option value="download_failed">다운로드 실패</option>
        <option value="extraction_failed">추출 실패</option>
      </select>
      <select value={query.enrichment_status ?? ''} onChange={(event) => update('enrichment_status', event.target.value)}>
        <option value="">AI 전체</option>
        <option value="pending">AI 요약 전</option>
        <option value="completed">AI 요약 완료</option>
      </select>
      <select value={query.sort ?? 'latest'} onChange={(event) => update('sort', event.target.value)}>
        <option value="latest">최근 수집순</option>
        <option value="price_asc">최저가 낮은순</option>
        <option value="price_desc">최저가 높은순</option>
        <option value="sale_date_asc">매각기일 빠른순</option>
      </select>
    </section>
  )
}
