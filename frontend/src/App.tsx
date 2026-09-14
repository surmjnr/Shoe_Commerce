import { FormEvent, useMemo, useState } from 'react';

import { Link, Route, Routes, useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { useMutation, useQuery } from '@tanstack/react-query';

import { useForm } from 'react-hook-form';

import { z } from 'zod';

import { zodResolver } from '@hookform/resolvers/zod';

import { createOrder, getProduct, getProductFilterOptions, trackOrder, type CreateOrderInput, type ProductFilters } from '@/services/storeApi';

import { getApiErrorMessage } from '@/lib/api/client';

import { useCartStore } from '@/stores/cart';

import type { ProductVariant } from '@/types';

import AdminApp from '@/components/admin/AdminApp';

import { Home } from '@/components/storefront/Home';

import { StorefrontLayout } from '@/components/storefront/StorefrontLayout';

import { ProductGrid } from '@/components/storefront/ProductGrid';

import { money } from '@/lib/format';



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

  const updateFilter = (key: keyof ProductFilters, value: string) => {

    const next = new URLSearchParams(searchParams);

    if (value && value.trim()) next.set(key, value.trim()); else next.delete(key);

    setSearchParams(next);

  };

  const clearFilters = () => {

    const next = new URLSearchParams(searchParams);

    ['brand', 'category', 'condition', 'color', 'size', 'min_price', 'max_price', 'search'].forEach((key) => next.delete(key));

    setSearchParams(next);

  };

  const activeFilters = Object.entries(filters).filter(([, value]) => Boolean(value)).map(([key, value]) => ({ key, value: String(value) }));

  const hasFilters = activeFilters.length > 0 || Boolean(searchValue);



  return <main className="container page"><div className="page-heading"><div><div className="eyebrow">Shop</div><h1 className="display">The collection</h1><p className="section-subtitle">Find your next everyday favorite from our considered edit.</p></div><button className="button secondary mobile-filter-toggle" type="button" onClick={() => setMobileOpen((value) => !value)}>Filters</button></div><div className="product-list-layout"><aside className={`product-filters ${mobileOpen ? 'open' : ''}`}>

    <div className="filter-header"><strong>Filters</strong>{mobileOpen ? <button type="button" className="text-button filter-close-button" onClick={() => setMobileOpen(false)} aria-label="Close filters">Close</button> : null}</div>

    <div className="filter-group"><label>Brand<select value={filters.brand || ''} onChange={(event) => updateFilter('brand', event.target.value)}><option value="">Any brand</option>{(filterOptions.data?.brands || []).map((option) => <option key={option.id} value={option.name}>{option.name}</option>)}</select></label></div>

    <div className="filter-group"><label>Category<select value={filters.category || ''} onChange={(event) => updateFilter('category', event.target.value)}><option value="">Any category</option>{(filterOptions.data?.categories || []).map((option) => <option key={option.id} value={option.name || option.value}>{option.name || option.value}</option>)}</select></label></div>

    <div className="filter-group"><label>Condition<select value={filters.condition || ''} onChange={(event) => updateFilter('condition', event.target.value)}><option value="">Any condition</option>{(filterOptions.data?.conditions || []).map((option) => <option key={option.id} value={option.name || option.value}>{option.name || option.value}</option>)}</select></label></div>

    <div className="filter-group"><label>Color<select value={filters.color || ''} onChange={(event) => updateFilter('color', event.target.value)}><option value="">Any color</option>{(filterOptions.data?.colors || []).map((option) => <option key={option.id} value={option.name}>{option.name}</option>)}</select></label></div>

    <div className="filter-group"><label>Size<select value={filters.size || ''} onChange={(event) => updateFilter('size', event.target.value)}><option value="">Any size</option>{(filterOptions.data?.sizes || []).map((option) => <option key={option.id} value={option.value}>{option.value}</option>)}</select></label></div>

    <div className="filter-grid"><label>Min price<input type="number" min="0" step="0.01" value={filters.min_price || ''} onChange={(event) => updateFilter('min_price', event.target.value)} placeholder="Min" /></label><label>Max price<input type="number" min="0" step="0.01" value={filters.max_price || ''} onChange={(event) => updateFilter('max_price', event.target.value)} placeholder="Max" /></label></div>

    <div className="filter-actions"><button type="button" className="button secondary" onClick={clearFilters}>Reset</button><button type="button" className="button" onClick={() => setMobileOpen(false)}>Apply filters</button></div>

  </aside>{mobileOpen && <button type="button" className="filter-backdrop" aria-label="Close filters" onClick={() => setMobileOpen(false)} />}

    <section className="products-main">{hasFilters && <div className="active-filters"><span>Applied:</span>{activeFilters.map(({ key, value }) => <button type="button" className="chip" key={key} onClick={() => updateFilter(key as keyof ProductFilters, '')}>{key.replace(/_/g, ' ')}: {value}</button>)}{searchValue && <button type="button" className="chip" onClick={() => { const next = new URLSearchParams(searchParams); next.delete('search'); setSearchParams(next); }}>search: {searchValue}</button>}</div>}<ProductGrid filters={filters} search={searchValue} /></section></div></main>;

}



function ProductDetail() {

  const { slug = '' } = useParams();

  const query = useQuery({ queryKey: ['product', slug], queryFn: () => getProduct(slug) });

  const addItem = useCartStore((state) => state.addItem);

  const [selected, setSelected] = useState<ProductVariant>();

  const [quantity, setQuantity] = useState(1);

  const [activeImage, setActiveImage] = useState(0);

  const [added, setAdded] = useState(false);

  if (query.isLoading) return <main className="container page"><div className="state state--loading"><span className="eyebrow">Product details</span><strong>Loading this pair...</strong></div></main>;

  if (query.isError || !query.data) return <main className="container page"><div className="state"><span className="eyebrow">Sorry</span><h1 className="display">Product not found.</h1><p>That pair may have moved on. Browse the collection to find another.</p><Link className="button" to="/products">Back to collection</Link></div></main>;

  const product = query.data;

  const variant = selected || product.variants?.find((entry) => entry.stock_quantity > 0);

  const images = product.images?.filter((image) => image.image_url).sort((a, b) => a.sort_order - b.sort_order).map((image) => image.image_url as string) || [];

  if (product.primary_image_url && !images.includes(product.primary_image_url)) images.unshift(product.primary_image_url);

  const image = images[activeImage] || product.primary_image_url;

  const add = () => { if (!variant) return; addItem({ productId: product.id, variantId: variant.id, productName: product.name, productSlug: product.slug, size: variant.size, price: product.price, quantity, imageUrl: product.primary_image_url, maxStock: variant.stock_quantity }); setAdded(true); };

  return <main className="container page"><div className="detail"><div className="detail-media"><div className="gallery-main">{image ? <img src={image} alt={`${product.name}, view ${activeImage + 1}`} /> : <span className="image-fallback">SOLE / HOUSE</span>}</div>{images.length > 1 && <div className="thumbnails">{images.map((source, index) => <button className={index === activeImage ? 'active' : ''} key={source} onClick={() => setActiveImage(index)} aria-label={`View image ${index + 1}`}><img src={source} alt="" /></button>)}</div>}</div><div className="detail-copy"><div className="eyebrow">{product.brand || product.category}</div><h1 className="display">{product.name}</h1><div className="price large-price">{money(product.price)}</div><p className="hero-copy">{product.description || 'A carefully selected pair for your everyday rotation.'}</p><div className="detail-rule" /><h3>Choose a size</h3><div className="variant-list">{product.variants?.map((entry) => <button type="button" className={`variant ${variant?.id === entry.id ? 'selected' : ''}`} disabled={!entry.stock_quantity} key={entry.id} onClick={() => { setSelected(entry); setQuantity(1); }}>{entry.size}{!entry.stock_quantity && <small>Sold out</small>}</button>)}</div>{variant && <div className="quantity"><span>Quantity</span><div><button type="button" onClick={() => setQuantity(Math.max(1, quantity - 1))} aria-label="Decrease quantity">−</button><strong>{quantity}</strong><button type="button" onClick={() => setQuantity(Math.min(variant.stock_quantity, quantity + 1))} aria-label="Increase quantity">+</button></div><span className="muted">{variant.stock_quantity} available</span></div>}<button className="button add-button" disabled={!variant} onClick={add}>{added ? 'Added to cart' : 'Add to cart'}</button>{added && <p className="added-note"><Link to="/cart">View cart and checkout ↗</Link></p>}<div className="delivery-note"><strong>Delivery & payment</strong><span>We deliver locally. Pay on delivery and Mobile Money are available at checkout.</span></div></div></div></main>;

}



function Cart() {

  const { items, updateQuantity, removeItem } = useCartStore();

  const subtotal = items.reduce((total, item) => total + Number(item.price) * item.quantity, 0);

  if (!items.length) return <main className="container page"><div className="state"><span className="eyebrow">Your bag</span><h1 className="display">Your cart is empty.</h1><p>There is plenty more to discover in the collection.</p><Link className="button" to="/products">Browse the collection</Link></div></main>;

  return <main className="container page"><div className="page-heading"><div><div className="eyebrow">Your bag</div><h1 className="display">Your cart</h1><p className="section-subtitle">Review your pairs before you make them yours.</p></div></div><div className="cart-layout"><div className="cart-items">{items.map((item) => <div className="cart-item" key={item.variantId}><div className="cart-item-image">{item.imageUrl ? <img src={item.imageUrl} alt="" /> : <span className="image-fallback">SOLE / HOUSE</span>}</div><div className="cart-item-copy"><div className="summary-row"><div><strong>{item.productName}</strong><span className="muted">Size {item.size} · {money(item.price)}</span></div><button className="text-button" onClick={() => removeItem(item.variantId)}>Remove</button></div><div className="summary-row cart-item-bottom"><label>Quantity <input type="number" min="1" max={item.maxStock} value={item.quantity} onChange={(event) => updateQuantity(item.variantId, Number(event.target.value))} /></label><strong>{money(Number(item.price) * item.quantity)}</strong></div></div></div>)}</div><aside className="checkout-summary"><span className="eyebrow">Order summary</span><div className="summary-row"><span>Subtotal</span><strong>{money(subtotal)}</strong></div><span className="muted">Delivery fee calculated with your order.</span><Link className="button" to="/checkout">Proceed to checkout</Link></aside></div></main>;

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

  if (!items.length) return <main className="container page"><div className="state"><span className="eyebrow">Checkout</span><h1 className="display">Your cart is empty.</h1><Link className="button" to="/products">Browse shoes</Link></div></main>;

  return <main className="container page"><div className="checkout-layout"><div><div className="eyebrow">Checkout</div><h1 className="display">Almost yours.</h1><p className="section-subtitle checkout-lead">Tell us where to send your new favorites.</p><form className="form checkout-form" onSubmit={handleSubmit(submit)}><label className="field">Full name<input {...register('buyer_name')} />{errors.buyer_name && <span className="error">{errors.buyer_name.message}</span>}</label><label className="field">Phone<input {...register('buyer_phone')} />{errors.buyer_phone && <span className="error">{errors.buyer_phone.message}</span>}</label><label className="field">Delivery address<textarea rows={3} {...register('delivery_address')} />{errors.delivery_address && <span className="error">{errors.delivery_address.message}</span>}</label><label className="field">Additional instructions<textarea rows={2} {...register('delivery_notes')} /></label><fieldset className="field payment-options"><legend>Payment</legend><label><input type="radio" value="PAY_ON_DELIVERY" {...register('payment_method')} /> <span><strong>Pay on delivery</strong><small>Pay when your order arrives.</small></span></label><label><input type="radio" value="MOMO" {...register('payment_method')} /> <span><strong>Mobile Money</strong><small>Complete payment with your mobile wallet.</small></span></label></fieldset>{error && <div className="error form-error">{error}</div>}<button className="button" disabled={mutation.isPending}>{mutation.isPending ? 'Placing order...' : 'Place order'}</button></form></div><OrderSummary /></div></main>;

}



function OrderSummary() { const items = useCartStore((state) => state.items); const subtotal = items.reduce((total, item) => total + Number(item.price) * item.quantity, 0); return <aside className="checkout-summary"><span className="eyebrow">Order summary</span>{items.map((item) => <div className="summary-row" key={item.variantId}><span>{item.productName} / {item.size} x{item.quantity}</span><span>{money(Number(item.price) * item.quantity)}</span></div>)}<div className="summary-row summary-total"><strong>Total before delivery</strong><strong>{money(subtotal)}</strong></div><span className="muted">Delivery fee is confirmed with your order.</span></aside>; }



function Confirmation() { const { orderNumber = '' } = useParams(); return <main className="container page"><div className="state confirmation-state"><span className="confirmation-mark" aria-hidden="true">✓</span><div className="eyebrow">Order received</div><h1 className="display">Thank you for your order.</h1><p>Order <strong>#{orderNumber}</strong> has been saved. We will confirm the next step with you.</p><div className="state-actions"><Link className="button" to={`/track?order=${orderNumber}`}>Track order</Link><Link className="button secondary" to="/products">Continue shopping</Link></div></div></main>; }



function Track() { const [orderNumber, setOrderNumber] = useState(''); const [phone, setPhone] = useState(''); const query = useQuery({ queryKey: ['track', orderNumber, phone], queryFn: () => trackOrder(orderNumber, phone), enabled: false }); const submit = (event: FormEvent) => { event.preventDefault(); void query.refetch(); }; return <main className="container page"><div className="tracking-layout"><div className="tracking-intro"><div className="eyebrow">Order tracking</div><h1 className="display">Where is your order?</h1><p className="section-subtitle">Enter the details from your confirmation and we’ll show the latest update.</p></div><div className="tracking-panel"><form className="form" onSubmit={submit}><label className="field">Order number<input value={orderNumber} onChange={(event) => setOrderNumber(event.target.value)} placeholder="SF12345678" required /></label><label className="field">Phone number<input value={phone} onChange={(event) => setPhone(event.target.value)} required /></label><button className="button" disabled={query.isFetching}>{query.isFetching ? 'Finding order...' : 'Find order'}</button></form>{query.isError && <div className="error form-error">{getApiErrorMessage(query.error)}</div>}{query.data && <div className="tracking-result"><div className="summary-row"><strong>Order #{query.data.order_number}</strong><span className="status status-pending">{query.data.order_status.replace(/_/g, ' ')}</span></div><strong className="tracking-total">{money(query.data.total)}</strong><div className="tracking-timeline">{query.data.status_timeline.map((step) => <div className={`timeline-step${step.completed ? ' completed' : ''}${step.current ? ' current' : ''}`} key={step.status}><span className="timeline-dot" /><div><strong>{step.status.replace(/_/g, ' ')}</strong><small>{step.completed ? 'Complete' : 'Pending'}</small></div></div>)}</div></div>}</div></div></main>; }



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

