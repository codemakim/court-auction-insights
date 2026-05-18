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
  minimum_sale_price: number | null
  sale_date: string | null
  current_status: string | null
  sale_spec_status: string
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
