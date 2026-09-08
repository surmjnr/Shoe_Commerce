import { apiClient } from '@/lib/api/client';
import type {
  AdminUser,
  AuthResponse,
  DashboardStats,
  Order,
  PaginatedResponse,
  Product,
  StoreSettings,
} from '@/types';

export type ProductInput = {
  name: string;
  description: string;
  brand: string;
  category: string;
  price: string;
  condition: string;
  color: string;
  status: string;
  is_featured: boolean;
  variants: Array<{ size: string; stock_quantity: number; sku: string; is_active: boolean }>;
};

export type ProductOption = { id: number; option_type: string; value: string; label: string; created_at: string };

export async function loginAdmin(email: string, password: string): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/admin/auth/login/', { email, password });
  localStorage.setItem('admin_access_token', response.data.access);
  localStorage.setItem('admin_refresh_token', response.data.refresh);
  return response.data;
}

export function logoutAdmin() {
  localStorage.removeItem('admin_access_token');
  localStorage.removeItem('admin_refresh_token');
}

export async function getAdminUser(): Promise<AdminUser> {
  const response = await apiClient.get<AdminUser>('/admin/auth/me/');
  return response.data;
}

export async function getDashboard(): Promise<DashboardStats> {
  const response = await apiClient.get<DashboardStats>('/admin/dashboard/');
  return response.data;
}

export async function getAdminProducts(): Promise<Product[]> {
  const response = await apiClient.get<PaginatedResponse<Product> | Product[]>('/admin/products/');
  return Array.isArray(response.data) ? response.data : response.data.results;
}

export async function createProduct(payload: ProductInput): Promise<Product> {
  const response = await apiClient.post<Product>('/admin/products/', payload);
  return response.data;
}

export async function updateProduct(id: number, payload: Partial<ProductInput>): Promise<Product> {
  const response = await apiClient.patch<Product>(`/admin/products/${id}/`, payload);
  return response.data;
}

export async function deleteProduct(id: number): Promise<void> {
  await apiClient.delete(`/admin/products/${id}/`);
}

export async function getAdminOrders(status = ''): Promise<Order[]> {
  const response = await apiClient.get<PaginatedResponse<Order> | Order[]>('/admin/orders/', {
    params: status ? { status } : {},
  });
  return Array.isArray(response.data) ? response.data : response.data.results;
}

export async function updateOrderStatus(id: number, status: string): Promise<Order> {
  const response = await apiClient.patch<Order>(`/admin/orders/${id}/status/`, { status });
  return response.data;
}

export async function markOrderPaid(id: number): Promise<Order> {
  const response = await apiClient.patch<Order>(`/admin/orders/${id}/payment/`);
  return response.data;
}

export async function getAdminSettings(): Promise<StoreSettings> {
  const response = await apiClient.get<StoreSettings>('/admin/settings/');
  return response.data;
}

export async function updateAdminSettings(payload: Partial<StoreSettings>): Promise<StoreSettings> {
  const response = await apiClient.patch<StoreSettings>('/admin/settings/', payload);
  return response.data;
}

export async function getProductOptions(optionType?: string): Promise<ProductOption[]> {
  const response = await apiClient.get<PaginatedResponse<ProductOption> | ProductOption[]>('/admin/options/', { params: optionType ? { option_type: optionType } : {} });
  return Array.isArray(response.data) ? response.data : response.data.results;
}

export async function createProductOption(payload: { option_type: string; value: string; label: string }): Promise<ProductOption> {
  const response = await apiClient.post<ProductOption>('/admin/options/', payload);
  return response.data;
}

export async function updateProductOption(id: number, payload: { value: string; label: string }): Promise<ProductOption> {
  const response = await apiClient.patch<ProductOption>(`/admin/options/${id}/`, payload);
  return response.data;
}

export async function deleteProductOption(id: number): Promise<void> {
  await apiClient.delete(`/admin/options/${id}/`);
}

export async function uploadProductImages(id: number, files: File[]): Promise<Product> {
  const payload = new FormData();
  files.forEach((file) => payload.append('images', file));
  const response = await apiClient.post<Product>(`/admin/products/${id}/images/`, payload, { headers: { 'Content-Type': 'multipart/form-data' } });
  return response.data;
}

export async function deleteProductImage(productId: number, imageId: number): Promise<void> {
  await apiClient.delete(`/admin/products/${productId}/images/${imageId}/`);
}