export interface ProductImage {
  id: number;
  image_url: string | null;
  alt_text: string;
  sort_order: number;
}

export interface ProductVariant {
  id: number;
  size: string;
  sku: string;
  stock_quantity: number;
  is_active: boolean;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description?: string;
  brand: string;
  category: string;
  price: string;
  color: string;
  condition?: string;
  status: string;
  is_featured: boolean;
  primary_image_url: string | null;
  available_sizes: string[];
  total_stock: number;
  images?: ProductImage[];
  variants?: ProductVariant[];
  created_at: string;
  updated_at?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Category {
  value: string;
  label: string;
}

export interface CartItem {
  productId: number;
  variantId: number;
  productName: string;
  productSlug: string;
  size: string;
  price: string;
  quantity: number;
  imageUrl: string | null;
  maxStock: number;
}

export interface OrderItem {
  id: number;
  product_name: string;
  size: string;
  quantity: number;
  unit_price: string;
  subtotal: string;
}

export interface Order {
  id: number;
  order_number: string;
  buyer_name: string;
  buyer_phone: string;
  delivery_address: string;
  delivery_notes: string;
  payment_method: 'MOMO' | 'PAY_ON_DELIVERY';
  payment_status: string;
  order_status: string;
  subtotal: string;
  delivery_fee: string;
  total: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface OrderTracking {
  order_number: string;
  order_status: string;
  payment_method: string;
  payment_status: string;
  total: string;
  items: OrderItem[];
  status_timeline: Array<{
    status: string;
    completed: boolean;
    current: boolean;
  }>;
  created_at: string;
  updated_at: string;
}

export interface StoreSettings {
  id: number;
  business_name: string;
  logo_url: string | null;
  description: string;
  phone: string;
  whatsapp_number: string;
  email: string;
  address: string;
  delivery_information: string;
  payment_information: string;
  currency: string;
  delivery_fee: string;
}

export interface AdminUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
}

export interface DashboardStats {
  total_products: number;
  total_orders: number;
  pending_orders: number;
  total_sales: string;
  recent_orders: Array<{
    id: number;
    order_number: string;
    buyer_name: string;
    buyer_phone: string;
    total: string;
    payment_method: string;
    payment_status: string;
    order_status: string;
    created_at: string;
  }>;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: AdminUser;
}
