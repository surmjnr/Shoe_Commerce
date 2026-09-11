import { Link } from 'react-router-dom';
import type { ProductFilters } from '@/services/storeApi';
import { ProductGrid } from './ProductGrid';

type ProductSectionProps = {
  eyebrow: string;
  title: string;
  subtitle?: string;
  linkTo: string;
  linkLabel?: string;
  filters?: ProductFilters;
  limit?: number;
};

export function ProductSection({
  eyebrow,
  title,
  subtitle,
  linkTo,
  linkLabel = 'View all ↗',
  filters,
  limit = 8,
}: ProductSectionProps) {
  return (
    <section className="section">
      <div className="section-head">
        <div>
          <div className="eyebrow">{eyebrow}</div>
          <h2>{title}</h2>
          {subtitle && <p className="section-subtitle">{subtitle}</p>}
        </div>
        <Link to={linkTo} className="section-link">
          {linkLabel}
        </Link>
      </div>
      <ProductGrid filters={filters} limit={limit} />
    </section>
  );
}
