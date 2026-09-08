import { FormEvent, useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createProduct,
  deleteProduct,
  getAdminOrders,
  getAdminProducts,
  getAdminSettings,
  getDashboard,
  loginAdmin,
  logoutAdmin,
  markOrderPaid,
  type ProductInput,
  updateAdminSettings,
  updateOrderStatus,
  updateProduct,
} from '@/services/adminApi';
import { getApiErrorMessage } from '@/lib/api/client';
import type { Order, Product, StoreSettings } from '@/types';
import ProductFormEditor from './ProductForm';
import Configuration from './Configuration';

const statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED'];
const categories = ['SNEAKERS', 'RUNNING', 'FORMAL', 'CASUAL', 'SANDALS', 'BOOTS', 'OTHER'];

const blankProduct: ProductInput = {
  name: '', description: '', brand: '', category: 'SNEAKERS', price: '', condition: 'NEW', color: '',
  status: 'DRAFT', is_featured: false, variants: [{ size: '', stock_quantity: 0, sku: '', is_active: true }],
};

function money(value: string | number) { return `GHS ${Number(value).toFixed(2)}`; }
function label(value: string) { return value.replace(/_/g, ' ').toLowerCase().replace(/(^|\s)\S/g, (char: string) => char.toUpperCase()); }

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const mutation = useMutation({ mutationFn: () => loginAdmin(email, password), onError: (reason) => setError(getApiErrorMessage(reason)) });
  const submit = (event: FormEvent) => { event.preventDefault(); setError(''); mutation.mutate(); };
  return <main className="admin-login"><div className="admin-login-panel"><div className="eyebrow">Sole / House · Seller workspace</div><h1 className="display">Run the store.</h1><p className="muted">Sign in to manage stock, orders, and the storefront.</p><form className="form" onSubmit={submit}><label className="field">Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label className="field">Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{error && <div className="error">{error}</div>}<button className="button" disabled={mutation.isPending}>{mutation.isPending ? 'Signing in...' : 'Sign in'}</button></form></div></main>;
}

function Overview({ onOrders }: { onOrders: () => void }) {
  const query = useQuery({ queryKey: ['admin-dashboard'], queryFn: getDashboard });
  if (query.isLoading) return <div className="admin-loading">Loading your store overview...</div>;
  if (query.isError || !query.data) return <div className="error">{getApiErrorMessage(query.error)}</div>;
  const stats = query.data;
  return <section><div className="admin-heading"><div><div className="eyebrow">Today at a glance</div><h1 className="display">Good business starts with a clear view.</h1></div><button className="button" onClick={onOrders}>Review orders</button></div><div className="metric-grid"><div className="metric"><span>Products</span><strong>{stats.total_products}</strong><small>listed in catalogue</small></div><div className="metric"><span>Orders</span><strong>{stats.total_orders}</strong><small>{stats.pending_orders} awaiting action</small></div><div className="metric"><span>Sales</span><strong>{money(stats.total_sales)}</strong><small>all-time recorded</small></div></div><div className="admin-section"><div className="section-head"><h2>Recent orders</h2><button className="text-button" onClick={onOrders}>View all</button></div><OrderTable orders={stats.recent_orders as Order[]} compact /></div></section>;
}

function OrderTable({ orders, compact = false }: { orders: Order[]; compact?: boolean }) {
  const queryClient = useQueryClient();
  const [error, setError] = useState('');
  const statusMutation = useMutation({ mutationFn: ({ id, status }: { id: number; status: string }) => updateOrderStatus(id, status), onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['admin-orders'] }); void queryClient.invalidateQueries({ queryKey: ['admin-dashboard'] }); }, onError: (reason) => setError(getApiErrorMessage(reason)) });
  const paidMutation = useMutation({ mutationFn: markOrderPaid, onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['admin-orders'] }); }, onError: (reason) => setError(getApiErrorMessage(reason)) });
  return <div className="table-wrap">{error && <div className="error">{error}</div>}<table><thead><tr><th>Order</th><th>Customer</th><th>Total</th><th>Status</th><th>Payment</th>{!compact && <th>Actions</th>}</tr></thead><tbody>{orders.length ? orders.map((order) => { const paymentStatus = order.payment_status || 'UNKNOWN'; return <tr key={order.id}><td><strong>{order.order_number}</strong><small>{new Date(order.created_at).toLocaleDateString()}</small></td><td>{order.buyer_name}<small>{order.buyer_phone}</small></td><td>{money(order.total)}</td><td><span className={`status status-${order.order_status.toLowerCase()}`}>{label(order.order_status)}</span></td><td><span className={`status status-${paymentStatus.toLowerCase()}`}>{label(paymentStatus)}</span></td>{!compact && <td><div className="table-actions"><select value={order.order_status} onChange={(event) => statusMutation.mutate({ id: order.id, status: event.target.value })}>{statuses.map((status) => <option key={status} value={status}>{label(status)}</option>)}</select>{paymentStatus !== 'PAID' && <button className="text-button" onClick={() => paidMutation.mutate(order.id)}>Mark paid</button>}</div></td>}</tr>; }) : <tr><td colSpan={compact ? 5 : 6} className="empty-cell">No orders yet.</td></tr>}</tbody></table></div>;
}

function Orders() {
  const [filter, setFilter] = useState('');
  const query = useQuery({ queryKey: ['admin-orders', filter], queryFn: () => getAdminOrders(filter) });
  return <section><div className="admin-heading"><div><div className="eyebrow">Fulfilment</div><h1 className="display">Orders</h1></div><select className="filter" value={filter} onChange={(event) => setFilter(event.target.value)}><option value="">All statuses</option>{statuses.map((status) => <option key={status} value={status}>{label(status)}</option>)}</select></div>{query.isLoading ? <div className="admin-loading">Loading orders...</div> : query.isError ? <div className="error">{getApiErrorMessage(query.error)}</div> : <OrderTable orders={query.data || []} />}</section>;
}

function LegacyProductForm({ product, onDone }: { product?: Product; onDone: () => void }) {
  const [form, setForm] = useState<ProductInput>(product ? { name: product.name, description: product.description || '', brand: product.brand, category: product.category, price: product.price, condition: product.condition || 'NEW', color: product.color, status: product.status, is_featured: product.is_featured, variants: product.variants?.map((variant) => ({ size: variant.size, stock_quantity: variant.stock_quantity, sku: variant.sku, is_active: variant.is_active })) || [] } : blankProduct);
  const [error, setError] = useState('');
  const queryClient = useQueryClient();
  const mutation = useMutation({ mutationFn: () => product ? updateProduct(product.id, form) : createProduct(form), onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['admin-products'] }); onDone(); }, onError: (reason) => setError(getApiErrorMessage(reason)) });
  const update = (key: keyof ProductInput, value: string | boolean) => setForm((current) => ({ ...current, [key]: value }));
  const updateVariant = (index: number, key: 'size' | 'stock_quantity' | 'sku', value: string) => setForm((current) => ({ ...current, variants: current.variants.map((variant, variantIndex) => variantIndex === index ? { ...variant, [key]: key === 'stock_quantity' ? Number(value) : value } : variant) }));
  const submit = (event: FormEvent) => { event.preventDefault(); setError(''); mutation.mutate(); };
  return <form className="admin-form" onSubmit={submit}><div className="form-grid"><label className="field">Product name<input value={form.name} onChange={(event) => update('name', event.target.value)} required /></label><label className="field">Brand<input value={form.brand} onChange={(event) => update('brand', event.target.value)} /></label><label className="field">Price<input type="number" min="0" step="0.01" value={form.price} onChange={(event) => update('price', event.target.value)} required /></label><label className="field">Category<select value={form.category} onChange={(event) => update('category', event.target.value)}>{categories.map((category) => <option key={category} value={category}>{label(category)}</option>)}</select></label><label className="field">Condition<select value={form.condition} onChange={(event) => update('condition', event.target.value)}>{['NEW', 'LIKE_NEW', 'USED'].map((condition) => <option key={condition} value={condition}>{label(condition)}</option>)}</select></label><label className="field">Visibility<select value={form.status} onChange={(event) => update('status', event.target.value)}>{['DRAFT', 'PUBLISHED', 'HIDDEN', 'OUT_OF_STOCK'].map((status) => <option key={status} value={status}>{label(status)}</option>)}</select></label></div><label className="field">Description<textarea rows={3} value={form.description} onChange={(event) => update('description', event.target.value)} /></label><label className="field">Color<input value={form.color} onChange={(event) => update('color', event.target.value)} /></label><label className="check"><input type="checkbox" checked={form.is_featured} onChange={(event) => update('is_featured', event.target.checked)} /> Feature this product</label><div><div className="subheading">Sizes and stock</div>{form.variants.map((variant, index) => <div className="variant-row" key={`${index}-${variant.size}`}><input placeholder="Size" value={variant.size} onChange={(event) => updateVariant(index, 'size', event.target.value)} required /><input type="number" min="0" placeholder="Stock" value={variant.stock_quantity} onChange={(event) => updateVariant(index, 'stock_quantity', event.target.value)} /><input placeholder="SKU (optional)" value={variant.sku} onChange={(event) => updateVariant(index, 'sku', event.target.value)} /><button type="button" className="icon-button" title="Remove size" onClick={() => setForm((current) => ({ ...current, variants: current.variants.filter((_, variantIndex) => variantIndex !== index) }))}>×</button></div>)}<button type="button" className="text-button" onClick={() => setForm((current) => ({ ...current, variants: [...current.variants, { size: '', stock_quantity: 0, sku: '', is_active: true }] }))}>+ Add size</button></div>{error && <div className="error">{error}</div>}<div className="form-actions"><button type="button" className="button secondary" onClick={onDone}>Cancel</button><button className="button" disabled={mutation.isPending}>{mutation.isPending ? 'Saving...' : product ? 'Save changes' : 'Add product'}</button></div></form>;
}

void LegacyProductForm;

function Products() {
  const [editing, setEditing] = useState<Product | undefined>();
  const [showForm, setShowForm] = useState(false);
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ['admin-products'], queryFn: getAdminProducts });
  const deleteMutation = useMutation({ mutationFn: deleteProduct, onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['admin-products'] }); } });
  if (showForm) return <section><div className="admin-heading"><div><div className="eyebrow">Catalogue</div><h1 className="display">{editing ? 'Edit product' : 'Add product'}</h1></div></div><ProductFormEditor product={editing} onDone={() => { setShowForm(false); setEditing(undefined); }} /></section>;
  return <section><div className="admin-heading"><div><div className="eyebrow">Catalogue</div><h1 className="display">Products</h1></div><button className="button" onClick={() => setShowForm(true)}>+ Add product</button></div>{query.isLoading ? <div className="admin-loading">Loading products...</div> : query.isError ? <div className="error">Could not load products.</div> : <div className="product-admin-grid">{(query.data || []).map((product) => <article className="product-admin-card" key={product.id}><div className="product-admin-image">{product.primary_image_url && <img src={product.primary_image_url} alt="" />}</div><div className="product-admin-body"><div className="card-topline"><span className={`status status-${product.status.toLowerCase()}`}>{label(product.status)}</span><span className="muted">{product.total_stock} in stock</span></div><h3>{product.name}</h3><p className="muted">{product.brand || label(product.category)} · {money(product.price)}</p><div className="card-actions"><button className="text-button" onClick={() => { setEditing(product); setShowForm(true); }}>Edit</button><button className="text-button danger" onClick={() => { if (window.confirm(`Delete ${product.name}?`)) deleteMutation.mutate(product.id); }}>Delete</button></div></div></article>)}</div>}</section>;
}

function Settings() {
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ['admin-settings'], queryFn: getAdminSettings });
  const [form, setForm] = useState<Partial<StoreSettings>>({});
  const mutation = useMutation({ mutationFn: () => updateAdminSettings(form), onSuccess: (data) => { setForm(data); void queryClient.invalidateQueries({ queryKey: ['store-settings'] }); } });
  useEffect(() => { if (query.data) setForm(query.data); }, [query.data]);
  const update = (key: keyof StoreSettings, value: string) => setForm((current) => ({ ...current, [key]: value }));
  if (query.isLoading || !query.data) return <div className="admin-loading">Loading store settings...</div>;
  return <section><div className="admin-heading"><div><div className="eyebrow">Storefront</div><h1 className="display">Store settings</h1></div></div><form className="admin-form settings-form" onSubmit={(event) => { event.preventDefault(); mutation.mutate(); }}><div className="form-grid"><label className="field">Business name<input value={form.business_name || ''} onChange={(event) => update('business_name', event.target.value)} /></label><label className="field">Phone<input value={form.phone || ''} onChange={(event) => update('phone', event.target.value)} /></label><label className="field">WhatsApp number<input value={form.whatsapp_number || ''} onChange={(event) => update('whatsapp_number', event.target.value)} /></label><label className="field">Email<input type="email" value={form.email || ''} onChange={(event) => update('email', event.target.value)} /></label><label className="field">Currency<input value={form.currency || ''} onChange={(event) => update('currency', event.target.value)} /></label><label className="field">Delivery fee<input type="number" min="0" step="0.01" value={form.delivery_fee || ''} onChange={(event) => update('delivery_fee', event.target.value)} /></label></div><label className="field">Address<textarea rows={2} value={form.address || ''} onChange={(event) => update('address', event.target.value)} /></label><label className="field">Store description<textarea rows={3} value={form.description || ''} onChange={(event) => update('description', event.target.value)} /></label><label className="field">Delivery information<textarea rows={3} value={form.delivery_information || ''} onChange={(event) => update('delivery_information', event.target.value)} /></label><label className="field">Payment information<textarea rows={3} value={form.payment_information || ''} onChange={(event) => update('payment_information', event.target.value)} /></label><div className="form-actions"><button className="button" disabled={mutation.isPending}>{mutation.isPending ? 'Saving...' : 'Save settings'}</button></div>{mutation.isError && <div className="error">{getApiErrorMessage(mutation.error)}</div>}{mutation.isSuccess && <div className="success">Settings saved.</div>}</form></section>;
}

export default function AdminApp() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem('admin_access_token')));
  const [tab, setTab] = useState<'overview' | 'products' | 'orders' | 'settings' | 'configuration'>('overview');
  if (!authenticated) return <Login />;
  const signOut = () => { logoutAdmin(); setAuthenticated(false); };
  return <div className="admin-shell"><aside className="admin-sidebar"><div className="admin-brand"><span className="eyebrow">Sole / House</span><strong>Seller workspace</strong></div><nav className="admin-nav" aria-label="Seller navigation">{[['overview', 'Overview'], ['products', 'Products'], ['orders', 'Orders'], ['settings', 'Settings'], ['configuration', 'Configuration']].map(([value, text]) => <button className={tab === value ? 'active' : ''} key={value} onClick={() => setTab(value as typeof tab)}>{text}</button>)}</nav><a className="admin-storefront-link" href="/" target="_blank" rel="noreferrer">View storefront ↗</a><button className="admin-signout" onClick={signOut}>Sign out</button></aside><main className="admin-main">{tab === 'overview' && <Overview onOrders={() => setTab('orders')} />}{tab === 'products' && <Products />}{tab === 'orders' && <Orders />}{tab === 'settings' && <Settings />}{tab === 'configuration' && <Configuration />}</main></div>;
}