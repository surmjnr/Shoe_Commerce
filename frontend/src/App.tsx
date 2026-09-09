import { FormEvent, ReactNode, useEffect, useMemo, useState } from 'react';
import { Link, Route, Routes, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { createOrder, getProduct, getProductFilterOptions, getProducts, getStoreSettings, trackOrder, type CreateOrderInput, type ProductFilters } from '@/services/storeApi';
import { getApiErrorMessage } from '@/lib/api/client';
import { useCartStore } from '@/stores/cart';
import type { Product, ProductVariant } from '@/types';
import AdminApp from '@/components/admin/AdminApp';

const money = (value: string | number) => `GHS ${Number(value).toFixed(2)}`;

function Header() {
  const count = useCartStore((state) => state.items.reduce((total, item) => total + item.quantity, 0));
  const settings = useQuery({ queryKey: ['store-settings'], queryFn: getStoreSettings });
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);
  return <header className="header"><div className="container header-inner">
    <button className="icon-button mobile-menu" aria-label="Open menu" aria-expanded={open} onClick={() => setOpen((value) => !value)}>☰</button>
    <Link className="logo" to="/" onClick={close}>{settings.data?.business_name || 'SOLE / HOUSE'}</Link>
    <nav className={`nav${open ? ' nav-open' : ''}`} aria-label="Main navigation"><button className="icon-button menu-close" aria-label="Close menu" onClick={close}>×</button><Link to="/products" onClick={close}>Shop</Link><Link to="/products?featured=true" onClick={close}>New arrivals</Link><Link to="/track" onClick={close}>Track order</Link></nav>
    <Link className="cart-link" to="/cart" aria-label={`Cart, ${count} items`}>Cart <span>{count}</span></Link>{open && <button className="menu-backdrop" aria-label="Close menu" onClick={close} />}
  </div></header>;
}

function ProductCard({ product }: { product: Product }) {
  const available = product.available_sizes?.filter(Boolean).join(' / ');
  return <Link className="product-card" to={`/products/${product.slug}`}>
    <div className="product-image"><span className="product-badge">{product.is_featured ? 'Featured' : ''}</span>{product.primary_image_url ? <img src={product.primary_image_url} alt={product.name} loading="lazy" /> : <span className="image-fallback">SOLE / HOUSE</span>}</div>
    <div className="product-meta"><span className="eyebrow">{product.brand || product.category}</span><h3>{product.name}</h3><div className="product-bottom"><span className="price">{money(product.price)}</span>{available && <span className="muted">{available}</span>}</div></div>
  </Link>;
}

function ProductGrid({ filters = {}, search = '' }: { filters?: ProductFilters; search?: string }) {
  const query = useQuery({ queryKey: ['products', { ...filters, search }], queryFn: () => getProducts({ ...filters, search }) });
  if (query.isLoading) return <div className="empty">Loading the collection...</div>;
  if (query.isError) return <div className="empty">We could not load the collection. Please try again.</div>;
  if (!query.data?.length) return <div className="empty">No shoes match the selected filters. Try adjusting your search or resetting the filters.</div>;
  return <div className="grid">{query.data.map((product) => <ProductCard key={product.id} product={product} />)}</div>;
}

function Home() {
  const [search, setSearch] = useState('');
  const products = useQuery({ queryKey: ['products', 'home'], queryFn: () => getProducts() });
  const submit = (event: FormEvent) => { event.preventDefault(); window.history.pushState({}, '', `/products${search ? `?search=${encodeURIComponent(search)}` : ''}`); window.dispatchEvent(new PopStateEvent('popstate')); };
  const categories = [...new Set((products.data || []).map((product) => product.category).filter(Boolean))].slice(0, 5);
  return <><main className="container">
    <section className="hero"><div><div className="eyebrow">Considered footwear / Accra</div><h1 className="display">Find your next pair.</h1><p className="hero-copy">Quality shoes, selected for everyday movement. Browse the current collection and order directly from our store.</p><div className="hero-actions"><Link className="button" to="/products">Shop collection</Link><Link className="button secondary" to="/products?featured=true">New arrivals</Link></div><form className="search" onSubmit={submit}><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search shoes by name or brand" aria-label="Search shoes" /><button className="button" type="submit">Search</button></form></div><div className="hero-panel"><span className="eyebrow">The edit</span><strong className="display">Built for the days you actually live.</strong><span>New pairs arrive regularly. Stock is updated at the source.</span></div></section>
    <section className="section"><div className="section-head"><div><div className="eyebrow">Browse your way</div><h2>Shop by category</h2></div></div><div className="category-grid">{categories.length ? categories.map((category) => <Link key={category} to={`/products?category=${encodeURIComponent(category)}`} className="category-tile"><span>{category.replace(/_/g, ' ')}</span><b>↗</b></Link>) : <p className="muted">Categories will appear as products are added.</p>}</div></section>
    <section className="section"><div className="section-head"><div><div className="eyebrow">Just in</div><h2>Latest collection</h2></div><Link to="/products">View all ↗</Link></div><ProductGrid /></section>
  </main></>;
}

function Products() {
  const [searchParams, setSearchParams] = useSearchParams();
  const filterOptions = useQuery({ queryKey: ['product-filter-options'], queryFn: getProductFilterOptions });
  const searchValue = searchParams.get('search') || '';
  const filters = useMemo<ProductFilters>(() => ({
    brand: searchParams.get('brand') || undefined,
    category: searchParams.get('category') || undefined,
    condition: searchParams.get('condition') || undefined,
    color: searchParams.get('color') || undefined,
    size: searchParams.get('size') || undefined,
    min_price: searchParams.get('min_price') || undefined,
    max_price: searchParams.get('max_price') || undefined,
  }), [searchParams]);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [draftSearch, setDraftSearch] = useState(searchValue);
  useEffect(() => setDraftSearch(searchValue), [searchValue]);
  const updateFilter = (key: keyof ProductFilters, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value && value.trim()) next.set(key, value.trim()); else next.delete(key);
    setSearchParams(next);
  };
  const applySearch = (event: FormEvent) => {
    event.preventDefault();
    const next = new URLSearchParams(searchParams);
    const trimmed = draftSearch.trim();
    if (trimmed) next.set('search', trimmed); else next.delete('search');
    setSearchParams(next);
  };
  const clearFilters = () => {
    const next = new URLSearchParams(searchParams);
    ['brand', 'category', 'condition', 'color', 'size', 'min_price', 'max_price', 'search'].forEach((key) => next.delete(key));
    setSearchParams(next);
  };
  const activeFilters = Object.entries(filters).filter(([, value]) => Boolean(value)).map(([key, value]) => ({ key, value }));
  const hasFilters = activeFilters.length > 0 || Boolean(searchValue);

  return <main className="container page"><div className="section-head"><div><div className="eyebrow">Shop</div><h1 className="display">The collection</h1></div><button className="button secondary mobile-filter-toggle" type="button" onClick={() => setMobileOpen((value) => !value)}>Filters</button></div><div className="product-list-layout"><aside className={`product-filters ${mobileOpen ? 'open' : ''}`}>
    <div className="filter-header"><strong>Filters</strong><button type="button" className="text-button" onClick={() => setMobileOpen(false)}>Close</button></div>
    <div className="filter-group"><label>Brand<select value={filters.brand || ''} onChange={(event) => updateFilter('brand', event.target.value)}><option value="">Any brand</option>{(filterOptions.data?.brands || []).map((option) => <option key={option.id} value={option.name}>{option.name}</option>)}</select></label></div>
    <div className="filter-group"><label>Category<select value={filters.category || ''} onChange={(event) => updateFilter('category', event.target.value)}><option value="">Any category</option>{(filterOptions.data?.categories || []).map((option) => <option key={option.id} value={option.name || option.value}>{option.name || option.value}</option>)}</select></label></div>
    <div className="filter-group"><label>Condition<select value={filters.condition || ''} onChange={(event) => updateFilter('condition', event.target.value)}><option value="">Any condition</option>{(filterOptions.data?.conditions || []).map((option) => <option key={option.id} value={option.name || option.value}>{option.name || option.value}</option>)}</select></label></div>
    <div className="filter-group"><label>Color<select value={filters.color || ''} onChange={(event) => updateFilter('color', event.target.value)}><option value="">Any color</option>{(filterOptions.data?.colors || []).map((option) => <option key={option.id} value={option.name}>{option.name}</option>)}</select></label></div>
    <div className="filter-group"><label>Size<select value={filters.size || ''} onChange={(event) => updateFilter('size', event.target.value)}><option value="">Any size</option>{(filterOptions.data?.sizes || []).map((option) => <option key={option.id} value={option.value}>{option.value}</option>)}</select></label></div>
    <div className="filter-grid"><label>Min price<input type="number" min="0" step="0.01" value={filters.min_price || ''} onChange={(event) => updateFilter('min_price', event.target.value)} placeholder="Min" /></label><label>Max price<input type="number" min="0" step="0.01" value={filters.max_price || ''} onChange={(event) => updateFilter('max_price', event.target.value)} placeholder="Max" /></label></div>
    <div className="filter-actions"><button type="button" className="button secondary" onClick={clearFilters}>Reset</button><button type="button" className="button" onClick={() => setMobileOpen(false)}>Apply filters</button></div>
  </aside>{mobileOpen && <button type="button" className="filter-backdrop" aria-label="Close filters" onClick={() => setMobileOpen(false)} />}
    <section className="products-main"><form className="search" onSubmit={applySearch}><input value={draftSearch} onChange={(event) => setDraftSearch(event.target.value)} placeholder="Search by name or brand" aria-label="Search products" /><button className="button" type="submit">Search</button></form>{hasFilters && <div className="active-filters"><span>Applied:</span>{activeFilters.map(({ key, value }) => <button type="button" className="chip" key={key} onClick={() => updateFilter(key as keyof ProductFilters, '')}>{key.replace(/_/g, ' ')}: {value}</button>)}{searchValue && <button type="button" className="chip" onClick={() => { const next = new URLSearchParams(searchParams); next.delete('search'); setSearchParams(next); }}>search: {searchValue}</button>}</div>}<ProductGrid filters={filters} search={searchValue} /></section></div></main>;
}

function ProductDetail() {
  const { slug = '' } = useParams();
  const query = useQuery({ queryKey: ['product', slug], queryFn: () => getProduct(slug) });
  const addItem = useCartStore((state) => state.addItem);
  const [selected, setSelected] = useState<ProductVariant>();
  const [quantity, setQuantity] = useState(1);
  const [activeImage, setActiveImage] = useState(0);
  const [added, setAdded] = useState(false);
  if (query.isLoading) return <main className="container page">Loading product...</main>;
  if (query.isError || !query.data) return <main className="container page"><div className="empty">Product not found.</div></main>;
  const product = query.data;
  const variant = selected || product.variants?.find((entry) => entry.stock_quantity > 0);
  const images = product.images?.filter((image) => image.image_url).sort((a, b) => a.sort_order - b.sort_order).map((image) => image.image_url as string) || [];
  if (product.primary_image_url && !images.includes(product.primary_image_url)) images.unshift(product.primary_image_url);
  const image = images[activeImage] || product.primary_image_url;
  const add = () => { if (!variant) return; addItem({ productId: product.id, variantId: variant.id, productName: product.name, productSlug: product.slug, size: variant.size, price: product.price, quantity, imageUrl: product.primary_image_url, maxStock: variant.stock_quantity }); setAdded(true); };
  return <main className="container page"><div className="detail"><div><div className="gallery-main">{image ? <img src={image} alt={`${product.name}, view ${activeImage + 1}`} /> : <span className="image-fallback">SOLE / HOUSE</span>}</div>{images.length > 1 && <div className="thumbnails">{images.map((source, index) => <button className={index === activeImage ? 'active' : ''} key={source} onClick={() => setActiveImage(index)} aria-label={`View image ${index + 1}`}><img src={source} alt="" /></button>)}</div>}</div><div className="detail-copy"><div className="eyebrow">{product.brand || product.category}</div><h1 className="display">{product.name}</h1><div className="price large-price">{money(product.price)}</div><p className="hero-copy">{product.description || 'A carefully selected pair for your everyday rotation.'}</p><div className="detail-rule" /><h3>Choose a size</h3><div className="variant-list">{product.variants?.map((entry) => <button type="button" className={`variant ${variant?.id === entry.id ? 'selected' : ''}`} disabled={!entry.stock_quantity} key={entry.id} onClick={() => { setSelected(entry); setQuantity(1); }}>{entry.size}{!entry.stock_quantity && <small>Sold out</small>}</button>)}</div>{variant && <div className="quantity"><span>Quantity</span><div><button type="button" onClick={() => setQuantity(Math.max(1, quantity - 1))} aria-label="Decrease quantity">−</button><strong>{quantity}</strong><button type="button" onClick={() => setQuantity(Math.min(variant.stock_quantity, quantity + 1))} aria-label="Increase quantity">+</button></div><span className="muted">{variant.stock_quantity} available</span></div>}<button className="button add-button" disabled={!variant} onClick={add}>{added ? 'Added to cart' : 'Add to cart'}</button>{added && <p><Link to="/cart">View cart and checkout ↗</Link></p>}<div className="delivery-note"><strong>Delivery & payment</strong><span>We deliver locally. Pay on delivery and Mobile Money are available at checkout.</span></div></div></div></main>;
}

function Cart() {
  const { items, updateQuantity, removeItem } = useCartStore();
  const subtotal = items.reduce((total, item) => total + Number(item.price) * item.quantity, 0);
  if (!items.length) return <main className="container page"><div className="empty"><h1 className="display">Your cart is empty.</h1><Link className="button" to="/products">Browse the collection</Link></div></main>;
  return <main className="container page"><div className="section-head"><h1 className="display">Your cart</h1></div><div className="form">{items.map((item) => <div className="summary" key={item.variantId}><div className="summary-row"><strong>{item.productName}</strong><button className="button secondary" onClick={() => removeItem(item.variantId)}>Remove</button></div><div className="muted">Size {item.size} · {money(item.price)}</div><div className="summary-row"><label>Quantity <input type="number" min="1" max={item.maxStock} value={item.quantity} onChange={(event) => updateQuantity(item.variantId, Number(event.target.value))} /></label><strong>{money(Number(item.price) * item.quantity)}</strong></div></div>)}<div className="summary-row"><strong>Subtotal</strong><strong>{money(subtotal)}</strong></div><Link className="button" to="/checkout">Proceed to checkout</Link></div></main>;
}

const checkoutSchema = z.object({ buyer_name: z.string().min(2, 'Enter your full name'), buyer_phone: z.string().min(7, 'Enter a valid phone number'), delivery_address: z.string().min(5, 'Enter your delivery address'), delivery_notes: z.string().optional(), payment_method: z.enum(['MOMO', 'PAY_ON_DELIVERY']) });
type CheckoutForm = z.infer<typeof checkoutSchema>;

function Checkout() {
  const navigate = useNavigate();
  const { items, clear } = useCartStore();
  const [error, setError] = useState('');
  const { register, handleSubmit, formState: { errors } } = useForm<CheckoutForm>({ resolver: zodResolver(checkoutSchema), defaultValues: { payment_method: 'PAY_ON_DELIVERY' } });
  const mutation = useMutation({ mutationFn: (payload: CreateOrderInput) => createOrder(payload), onSuccess: (order) => { clear(); navigate(`/order/${order.order_number}`, { state: { order } }); }, onError: (reason) => setError(getApiErrorMessage(reason)) });
  const submit = (data: CheckoutForm) => { setError(''); mutation.mutate({ ...data, items: items.map((item) => ({ product_id: item.productId, variant_id: item.variantId, quantity: item.quantity })) }); };
  if (!items.length) return <main className="container page"><div className="empty">Your cart is empty. <Link to="/products">Browse shoes</Link></div></main>;
  return <main className="container page"><div className="detail"><div><div className="eyebrow">Checkout</div><h1 className="display">Almost yours.</h1><form className="form" onSubmit={handleSubmit(submit)}><label className="field">Full name<input {...register('buyer_name')} />{errors.buyer_name && <span className="error">{errors.buyer_name.message}</span>}</label><label className="field">Phone<input {...register('buyer_phone')} />{errors.buyer_phone && <span className="error">{errors.buyer_phone.message}</span>}</label><label className="field">Delivery address<textarea rows={3} {...register('delivery_address')} />{errors.delivery_address && <span className="error">{errors.delivery_address.message}</span>}</label><label className="field">Additional instructions<textarea rows={2} {...register('delivery_notes')} /></label><fieldset className="field"><legend>Payment</legend><label><input type="radio" value="PAY_ON_DELIVERY" {...register('payment_method')} /> Pay on delivery</label><label><input type="radio" value="MOMO" {...register('payment_method')} /> Mobile Money</label></fieldset>{error && <div className="error">{error}</div>}<button className="button" disabled={mutation.isPending}>{mutation.isPending ? 'Placing order...' : 'Place order'}</button></form></div><OrderSummary /></div></main>;
}

function OrderSummary() { const items = useCartStore((state) => state.items); const subtotal = items.reduce((total, item) => total + Number(item.price) * item.quantity, 0); return <aside className="hero-panel"><span className="eyebrow">Order summary</span>{items.map((item) => <div className="summary-row" key={item.variantId}><span>{item.productName} / {item.size} x{item.quantity}</span><span>{money(Number(item.price) * item.quantity)}</span></div>)}<div className="summary-row"><strong>Total before delivery</strong><strong>{money(subtotal)}</strong></div></aside>; }

function Confirmation() { const { orderNumber = '' } = useParams(); return <main className="container page"><div className="empty"><div className="eyebrow">Order received</div><h1 className="display">Thank you for your order.</h1><p>Order <strong>#{orderNumber}</strong> has been saved. We will confirm the next step with you.</p><Link className="button" to={`/track?order=${orderNumber}`}>Track order</Link></div></main>; }

function Track() { const [orderNumber, setOrderNumber] = useState(''); const [phone, setPhone] = useState(''); const query = useQuery({ queryKey: ['track', orderNumber, phone], queryFn: () => trackOrder(orderNumber, phone), enabled: false }); const submit = (event: FormEvent) => { event.preventDefault(); void query.refetch(); }; return <main className="container page"><div className="form"><div className="eyebrow">Order tracking</div><h1 className="display">Where is my order?</h1><form className="form" onSubmit={submit}><label className="field">Order number<input value={orderNumber} onChange={(event) => setOrderNumber(event.target.value)} placeholder="SF12345678" required /></label><label className="field">Phone number<input value={phone} onChange={(event) => setPhone(event.target.value)} required /></label><button className="button">Find order</button></form>{query.isError && <div className="error">{getApiErrorMessage(query.error)}</div>}{query.data && <div className="summary"><strong>Order #{query.data.order_number}</strong><span>{query.data.order_status.replace(/_/g, ' ')}</span><strong>{money(query.data.total)}</strong>{query.data.status_timeline.map((step) => <div className="summary-row" key={step.status}><span>{step.status.replace(/_/g, ' ')}</span><span>{step.completed ? 'Complete' : 'Pending'}</span></div>)}</div>}</div></main>; }


function StorefrontLayout({ children }: { children: ReactNode }) {
  return <div className="shell"><Header />{children}<footer className="footer"><div className="container">Direct ordering for a single independent shoe store.</div></footer></div>;
}

export default function App() {
  return <Routes>
    <Route path="/admin/*" element={<AdminApp />} />
    <Route path="/" element={<StorefrontLayout><Home /></StorefrontLayout>} />
    <Route path="/products" element={<StorefrontLayout><Products /></StorefrontLayout>} />
    <Route path="/products/:slug" element={<StorefrontLayout><ProductDetail /></StorefrontLayout>} />
    <Route path="/cart" element={<StorefrontLayout><Cart /></StorefrontLayout>} />
    <Route path="/checkout" element={<StorefrontLayout><Checkout /></StorefrontLayout>} />
    <Route path="/order/:orderNumber" element={<StorefrontLayout><Confirmation /></StorefrontLayout>} />
    <Route path="/track" element={<StorefrontLayout><Track /></StorefrontLayout>} />
    <Route path="*" element={<StorefrontLayout><Home /></StorefrontLayout>} />
  </Routes>;
}
