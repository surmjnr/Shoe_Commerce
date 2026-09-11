import { Link } from 'react-router-dom';
import { formatCategory } from '@/lib/format';

export type CategoryWithImage = {
  name: string;
  imageUrl: string | null;
  productCount: number;
  featured?: boolean;
};

type CategoryCardProps = {
  category: CategoryWithImage;
};

export function CategoryCard({ category }: CategoryCardProps) {
  const label = formatCategory(category.name);

  return (
    <Link
      to={`/products?category=${encodeURIComponent(category.name)}`}
      className={`category-card${category.featured ? ' category-card--featured' : ''}`}
    >
      <div className="category-card__media">
        {category.imageUrl ? (
          <img src={category.imageUrl} alt="" loading="lazy" />
        ) : (
          <span className="category-card__placeholder">{label.slice(0, 1)}</span>
        )}
        <div className="category-card__overlay" aria-hidden="true" />
      </div>
      <div className="category-card__content">
        <h3>{label}</h3>
        <span className="category-card__count">
          {category.productCount} {category.productCount === 1 ? 'style' : 'styles'}
        </span>
      </div>
      <span className="category-card__arrow" aria-hidden="true">
        ↗
      </span>
    </Link>
  );
}
