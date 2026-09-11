import { Link } from 'react-router-dom';
import type { Product } from '@/types';
import { formatCategory, money } from '@/lib/format';

type FeaturedProductShowcaseProps = {
  product?: Product | null;
  loading?: boolean;
};

export function FeaturedProductShowcase({ product, loading }: FeaturedProductShowcaseProps) {
  if (loading) {
    return (
      <div className="featured-showcase featured-showcase--loading" aria-hidden="true">
        <div className="featured-showcase__shimmer" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="featured-showcase featured-showcase--empty">
        <span className="featured-showcase__badge">Featured</span>
        <div className="featured-showcase__copy">
          <strong className="featured-showcase__title">Curated footwear</strong>
          <p className="featured-showcase__text">New pairs arrive regularly. Browse the full collection.</p>
          <Link className="button featured-showcase__cta" to="/products">
            Shop collection
          </Link>
        </div>
      </div>
    );
  }

  const badge = product.is_featured ? 'Featured' : 'New arrival';
  const inStock = product.total_stock > 0;

  return (
    <article className="featured-showcase">
      <div className="featured-showcase__glow" aria-hidden="true" />
      <span className="featured-showcase__badge">{badge}</span>

      <div className="featured-showcase__media">
        {product.primary_image_url ? (
          <img src={product.primary_image_url} alt={product.name} className="featured-showcase__image" />
        ) : (
          <span className="image-fallback featured-showcase__fallback">SOLE / HOUSE</span>
        )}
      </div>

      <div className="featured-showcase__body">
        <span className="eyebrow">{product.brand || formatCategory(product.category)}</span>
        <h2 className="featured-showcase__title">{product.name}</h2>
        <div className="featured-showcase__meta">
          <span className="price featured-showcase__price">{money(product.price)}</span>
          <span className={`stock-pill${inStock ? '' : ' stock-pill--out'}`}>
            {inStock ? 'In stock' : 'Sold out'}
          </span>
        </div>
        <Link className="button featured-showcase__cta" to={`/products/${product.slug}`}>
          Shop now
        </Link>
      </div>
    </article>
  );
}
