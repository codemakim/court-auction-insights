import type { Auction, AuctionQuery, AuctionSummary } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

function buildQueryString(query: AuctionQuery) {
  const params = new URLSearchParams()
  Object.entries(query).forEach(([key, value]) => {
    if (value) params.set(key, value)
  })
  const serialized = params.toString()
  return serialized ? `?${serialized}` : ''
}

export async function fetchSummary(): Promise<AuctionSummary> {
  const response = await fetch(`${API_BASE_URL}/api/summary`)
  if (!response.ok) throw new Error('failed to load auction summary')
  return response.json()
}

export async function fetchAuctions(query: AuctionQuery): Promise<Auction[]> {
  const response = await fetch(`${API_BASE_URL}/api/auctions${buildQueryString(query)}`)
  if (!response.ok) throw new Error('failed to load auctions')
  return response.json()
}

export async function fetchAuctionDetail(id: number): Promise<Auction> {
  const response = await fetch(`${API_BASE_URL}/api/auctions/${id}`)
  if (!response.ok) throw new Error('failed to load auction detail')
  return response.json()
}

export function mediaUrl(path: string) {
  return `${API_BASE_URL}${path}`
}
