export type AuctionImage = {
  image_index: number
  alt_text: string | null
  url: string
}

export type Enrichment = {
  summary_title: string | null
  summary_bullets_json: string | null
  risk_label: string | null
  risk_comment: string | null
} | null

export type Auction = {
  id: number
  external_key: string
  case_number: string
  item_number: string
  address: string
  property_category: string
  residential_subtype: string | null
  district: string | null
  appraisal_value: number | null
  minimum_sale_price: number | null
  failed_auction_count: number | null
  sale_date: string | null
  current_status: string | null
  appraisal_summary: string | null
  area_note: string | null
  sale_spec_status: string
  sale_spec_error: string | null
  sale_spec_markdown: string | null
  discount_rate: number | null
  price_gap: number | null
  image_count: number
  enrichment_status: 'pending' | 'completed'
  enrichment: Enrichment
  images: AuctionImage[]
}

export type AuctionQuery = {
  q?: string
  district?: string
  subtype?: string
  min_price?: string
  max_price?: string
  sale_spec_status?: string
  enrichment_status?: string
  sort?: string
}

export type AuctionSummary = {
  total_count: number
  sale_spec_status_counts: Record<string, number>
  enrichment_status_counts: Record<string, number>
  district_counts: Record<string, number>
  subtype_counts: Record<string, number>
  districts: string[]
  subtypes: string[]
  image_count: number
  min_price: number | null
  max_price: number | null
}
