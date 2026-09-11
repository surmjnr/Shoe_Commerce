import { FormEvent, useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getStoreSettings } from '@/services/storeApi';
import { useCartStore } from '@/stores/cart';

const customerNavItems = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Shop', end: false },
  { to: '/products?featured=true', label: 'New arrivals', end: false },
  { to: '/track', label: 'Track order', end: false },
];

export function Header() {
  const count = useCartStore((state) => state.items.reduce((total, item) => total + item.quantity, 0));
  const settings = useQuery({ queryKey: ['store-settings'], queryFn: getStoreSettings });
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();
  const close = () => setOpen(false);

  const submitSearch = (event: FormEvent) => {
    event.preventDefault();
    close();
    const trimmed = search.trim();
    navigate(trimmed ? `/products?search=${encodeURIComponent(trimmed)}` : '/products');
  };

  return (
    <header className="header">
      <div className="container header-inner">
        <button
          type="button"
          className="icon-button mobile-menu"
          aria-label="Open menu"
          aria-controls="main-navigation"
          aria-expanded={open}
          onClick={() => setOpen((value) => !value)}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          </svg>
        </button>

        <Link className="logo" to="/" onClick={close}>
          {settings.data?.logo_url ? (
            <img src={settings.data.logo_url} alt={settings.data.business_name} className="logo-image" />
          ) : (
            settings.data?.business_name || 'SOLE / HOUSE'
          )}
        </Link>

        <nav id="main-navigation" className={`nav${open ? ' nav-open' : ''}`} aria-label="Main navigation">
          <button type="button" className="icon-button menu-close" aria-label="Close menu" onClick={close}>
            ×
          </button>
          {customerNavItems.map(({ to, label, end }) => (
            <NavLink key={to} to={to} end={end} onClick={close} className={({ isActive }) => (isActive ? 'active' : '')}>
              {label}
            </NavLink>
          ))}
        </nav>

        <form className="header-search" onSubmit={submitSearch}>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search shoes..."
            aria-label="Search shoes"
          />
          <button type="submit" className="header-search-btn" aria-label="Search">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" />
              <path d="M20 20l-3-3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>
        </form>

        <Link className="cart-link" to="/cart" aria-label={`Cart, ${count} items`} onClick={close}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M6 6h15l-1.5 9h-12L6 6zm0 0L5 3H2"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="9" cy="20" r="1.2" fill="currentColor" />
            <circle cx="18" cy="20" r="1.2" fill="currentColor" />
          </svg>
          <span className="cart-label">Cart</span>
          {count > 0 && <span className="cart-count">{count}</span>}
        </Link>

        {open && <button type="button" className="menu-backdrop" aria-label="Close menu" onClick={close} />}
      </div>
    </header>
  );
}
