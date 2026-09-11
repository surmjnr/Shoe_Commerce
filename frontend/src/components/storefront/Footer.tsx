import { Link } from 'react-router-dom';
import type { StoreSettings } from '@/types';

type FooterProps = {
  settings?: StoreSettings;
};

export function Footer({ settings }: FooterProps) {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div className="footer-brand">
          <strong>{settings?.business_name || 'SOLE / HOUSE'}</strong>
          <p>{settings?.description || 'Premium footwear for everyday style. Order directly from our store.'}</p>
        </div>
        <div className="footer-links">
          <div>
            <h4>Shop</h4>
            <Link to="/products">All products</Link>
            <Link to="/#categories">Categories</Link>
          </div>
          <div>
            <h4>Support</h4>
            <Link to="/track">Track order</Link>
            {settings?.phone && <a href={`tel:${settings.phone}`}>{settings.phone}</a>}
            {settings?.email && <a href={`mailto:${settings.email}`}>{settings.email}</a>}
          </div>
        </div>
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} {settings?.business_name || 'SOLE / HOUSE'}. All rights reserved.</span>
        </div>
      </div>
    </footer>
  );
}
