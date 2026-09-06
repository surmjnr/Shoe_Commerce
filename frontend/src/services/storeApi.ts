import { apiClient } from '@/lib/api/client';
import type { Order, OrderTracking, PaginatedResponse, Product, StoreSettings } from '@/types';

type ProductResponse = PaginatedResponse<Product> | Product[];

function results(response: ProductResponse): Product[] {
  return Array.isArray(response) ? response : response.results;
}

export async function getProducts(search = ''): Promise<Product[]> {
  const response = await apiClient.get<ProductResponse>('/products/', { params: search ? { search } : {} });
  return results(response.data);
}

export async function getProduct(slug: string): Promise<Product> {
  const response = await apiClient.get<Product>(`/products/${slug}/`);
  return response.data;
}

export async function getStoreSettings(): Promise<StoreSettings> {
  const response = await apiClient.get<StoreSettings>('/settings/');
  return response.data;
}

export type CreateOrderInput = {
  buyer_name: string;
  buyer_phone: string;
  delivery_address: string;
  delivery_notes?: string;
  payment_method: 'MOMO' | 'PAY_ON_DELIVERY';
  items: Array<{ product_id: number; variant_id: number; quantity: number }>;
};

export async function createOrder(payload: CreateOrderInput): Promise<Order> {
  const response = await apiClient.post<Order>('/orders/', payload);
  return response.data;
}

export async function trackOrder(order_number: string, phone: string): Promise<OrderTracking> {
  const response = await apiClient.post<OrderTracking>('/orders/track/', { order_number, phone });
  return response.data;
}
