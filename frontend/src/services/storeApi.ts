import { apiClient } from '@/lib/api/client';
import type { Order, OrderTracking, PaginatedResponse, Product, StoreSettings } from '@/types';

type ProductResponse = PaginatedResponse<Product> | Product[];
export type ProductFilters = {
  search?: string;
  brand?: string;
  category?: string;
  condition?: string;
  color?: string;
  size?: string;
  min_price?: number | string;
  max_price?: number | string;
  featured?: boolean | string;
};

export type FilterOption = { id: number; name: string; value?: string };

function results(response: ProductResponse): Product[] {
  return Array.isArray(response) ? response : response.results;
}

export async function getProducts(filters: ProductFilters = {}): Promise<Product[]> {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value !== undefined && value !== null && value !== ''),
  );
  const response = await apiClient.get<ProductResponse>('/products/', { params });
  return results(response.data);
}

export async function getProductFilterOptions(): Promise<{ brands: FilterOption[]; categories: FilterOption[]; conditions: FilterOption[]; colors: FilterOption[]; sizes: FilterOption[] }> {
  const [brands, categories, conditions, colors, sizes] = await Promise.all([
    apiClient.get<FilterOption[]>('/brands/'),
    apiClient.get<FilterOption[]>('/categories/'),
    apiClient.get<FilterOption[]>('/conditions/'),
    apiClient.get<FilterOption[]>('/colors/'),
    apiClient.get<FilterOption[]>('/sizes/'),
  ]);
  return {
    brands: brands.data,
    categories: categories.data,
    conditions: conditions.data,
    colors: colors.data,
    sizes: sizes.data,
  };
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
