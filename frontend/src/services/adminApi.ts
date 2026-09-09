import { apiClient } from '@/lib/api/client';
import type { AdminUser, AuthResponse, DashboardStats, Order, PaginatedResponse, Product, StoreSettings } from '@/types';

export type ProductInput = {
  name: string;
  description: string;
  brand: number | null;
  category: number | null;
  price: string;
  condition: number | null;
  color: number | null;
  status: string;
  is_featured: boolean;
  variants: Array<{ size: number; stock_quantity: number; sku: string; is_active: boolean }>;
};

export type ConfigurationOption = { id: number; name: string; value?: string; created_at: string; updated_at: string };
export type AdminProduct = Omit<Product, 'brand' | 'category' | 'condition' | 'color' | 'variants'> & {
  brand: number | null; brand_name: string | null;
  category: number | null; category_name: string | null;
  condition: number | null; condition_name: string | null;
  color: number | null; color_name: string | null;
  variants?: Array<{ id: number; size: number; sku: string; stock_quantity: number; is_active: boolean }>;
};

export async function loginAdmin(email: string, password: string): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/admin/auth/login/', { email, password });
  localStorage.setItem('admin_access_token', response.data.access);
  localStorage.setItem('admin_refresh_token', response.data.refresh);
  return response.data;
}
export function logoutAdmin() { localStorage.removeItem('admin_access_token'); localStorage.removeItem('admin_refresh_token'); }
export async function getAdminUser(): Promise<AdminUser> { return (await apiClient.get<AdminUser>('/admin/auth/me/')).data; }
export async function getDashboard(): Promise<DashboardStats> { return (await apiClient.get<DashboardStats>('/admin/dashboard/')).data; }
export async function getAdminProducts(): Promise<AdminProduct[]> {
  const response = await apiClient.get<PaginatedResponse<AdminProduct> | AdminProduct[]>('/admin/products/');
  return Array.isArray(response.data) ? response.data : response.data.results;
}
export async function createProduct(payload: ProductInput): Promise<Product> { return (await apiClient.post<Product>('/admin/products/', payload)).data; }
export async function updateProduct(id: number, payload: Partial<ProductInput>): Promise<Product> { return (await apiClient.patch<Product>(`/admin/products/${id}/`, payload)).data; }
export async function deleteProduct(id: number): Promise<void> { await apiClient.delete(`/admin/products/${id}/`); }
export type AdminOrderFilters = {
  status?: string;
  payment_status?: string;
  payment_method?: string;
  search?: string;
};

export async function getAdminOrders(filters: AdminOrderFilters = {}): Promise<Order[]> {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value !== undefined && value !== null && value !== ''),
  );
  const response = await apiClient.get<PaginatedResponse<Order> | Order[]>('/admin/orders/', { params });
  return Array.isArray(response.data) ? response.data : response.data.results;
}
export async function updateOrderStatus(id: number, status: string): Promise<Order> { return (await apiClient.patch<Order>(`/admin/orders/${id}/status/`, { status })).data; }
export async function markOrderPaid(id: number): Promise<Order> { return (await apiClient.patch<Order>(`/admin/orders/${id}/payment/`)).data; }
export async function getAdminSettings(): Promise<StoreSettings> { return (await apiClient.get<StoreSettings>('/admin/settings/')).data; }
export async function updateAdminSettings(payload: Partial<StoreSettings>): Promise<StoreSettings> { return (await apiClient.patch<StoreSettings>('/admin/settings/', payload)).data; }

async function getConfiguration<T extends ConfigurationOption>(path: string): Promise<T[]> {
  const response = await apiClient.get<PaginatedResponse<T> | T[]>(path);
  return Array.isArray(response.data) ? response.data : response.data.results;
}
export function getProductConfiguration() {
  return Promise.all([
    getConfiguration('/admin/configuration/brands/'), getConfiguration('/admin/configuration/categories/'),
    getConfiguration('/admin/configuration/conditions/'), getConfiguration('/admin/configuration/colors/'),
    getConfiguration('/admin/configuration/sizes/'),
  ]).then(([brands, categories, conditions, colors, sizes]) => ({ brands, categories, conditions, colors, sizes }));
}
const configurationPaths: Record<string, string> = { BRAND: 'brands', CATEGORY: 'categories', CONDITION: 'conditions', COLOR: 'colors', SIZE: 'sizes' };
function configurationPayload(type: string, value: string) {
  if (type === 'CATEGORY' || type === 'CONDITION') return { value: value.toUpperCase().replace(/\s+/g, '_'), name: value };
  return type === 'SIZE' ? { value } : { name: value };
}
export async function createConfiguration(type: string, value: string): Promise<ConfigurationOption> { return (await apiClient.post<ConfigurationOption>(`/admin/configuration/${configurationPaths[type]}/`, configurationPayload(type, value))).data; }
export async function updateConfiguration(type: string, id: number, value: string): Promise<ConfigurationOption> { return (await apiClient.patch<ConfigurationOption>(`/admin/configuration/${configurationPaths[type]}/${id}/`, configurationPayload(type, value))).data; }
export async function deleteConfiguration(type: string, id: number): Promise<void> { await apiClient.delete(`/admin/configuration/${configurationPaths[type]}/${id}/`); }
export async function uploadProductImages(id: number, files: File[]): Promise<Product> {
  const payload = new FormData(); files.forEach((file) => payload.append('images', file));
  return (await apiClient.post<Product>(`/admin/products/${id}/images/`, payload, { headers: { 'Content-Type': 'multipart/form-data' } })).data;
}
export async function deleteProductImage(productId: number, imageId: number): Promise<void> { await apiClient.delete(`/admin/products/${productId}/images/${imageId}/`); }
