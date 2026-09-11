import { MouseEvent } from 'react';
import { Link } from 'react-router-dom';
import type { Product } from '@/types';
import { formatCategory, money } from '@/lib/format';
import { useCartStore } from '@/stores/cart';

type ProductCardProps = {
  product: Product;
};

export function ProductCard({ product }: ProductCardProps) {
  const addItem = useCartStore((state) => state.addItem);
  const availableVariant = product.variants?.find((variant) => variant.stock_quantity > 0);
  const inStock = product.total_stock > 0;
  const available = product.available_sizes?.filter(Boolean).slice(0, 3).join(' · ');

  const quickAdd = (event: MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    if (!availableVariant) return;
    addItem({
      productId: product.id,
      variantId: availableVariant.id,
      productName: product.name,
      productSlug: product.slug,
      size: availableVariant.size,
      price: product.price,
      quantity: 1,
      imageUrl: product.primary_image_url,
      maxStock: availableVariant.stock_quantity,
    });
  };

  return (
    <article className="product-card-wrap">
      <Link className="product-card" to={`/products/${product.slug}`}>
        <div className="product-image">
          {product.is_featured && <span className="product-badge">Featured</span>}
          {!inStock && <span className="product-badge product-badge--muted">Sold out</span>}
          {product.primary_image_url ? (
            <img src={product.primary_image_url} alt={product.name} loading="lazy" />
          ) : (
            <span className="image-fallback">SOLE / HOUSE</span>
          )}
        </div>
        <div className="product-meta">
          <span className="eyebrow">{product.brand || formatCategory(product.category)}</span>
          <h3>{product.name}</h3>
          <div className="product-bottom">
            <span className="price">{money(product.price)}</span>
            {available && <span className="muted product-sizes">{available}</span>}
          </div>
        </div>
      </Link>
      {inStock && availableVariant && (
        <button type="button" className="product-quick-add" onClick={quickAdd}>
          Quick add
        </button>
      )}
    </article>
  );
}
