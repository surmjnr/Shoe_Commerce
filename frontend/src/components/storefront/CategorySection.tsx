import { Link } from 'react-router-dom';
import { CategoryCard, type CategoryWithImage } from './CategoryCard';

type CategorySectionProps = {
  categories: CategoryWithImage[];
  loading?: boolean;
};

export function CategorySection({ categories, loading }: CategorySectionProps) {
  if (loading) {
    return (
      <section className="section category-section">
        <div className="category-section__panel">
          <div className="section-head">
            <div>
              <div className="eyebrow">Browse your way</div>
              <h2>Shop by category</h2>
            </div>
          </div>
          <div className="category-card-grid category-card-grid--loading">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="category-card category-card--skeleton" aria-hidden="true" />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (!categories.length) {
    return (
      <section className="section category-section">
        <div className="category-section__panel">
          <div className="section-head">
            <div>
              <div className="eyebrow">Browse your way</div>
              <h2>Shop by category</h2>
            </div>
          </div>
          <p className="muted">Categories will appear as products are added to the store.</p>
        </div>
      </section>
    );
  }

  const featured = categories[0] ? { ...categories[0], featured: true } : null;
  const rest = categories.slice(1);

  return (
    <section className="section category-section" id="categories">
      <div className="category-section__panel">
        <div className="section-head">
          <div>
            <div className="eyebrow">Browse your way</div>
            <h2>Shop by category</h2>
            <p className="section-subtitle">Find the perfect pair for every occasion</p>
          </div>
          <Link to="/products" className="section-link">
            View all ↗
          </Link>
        </div>

        <div className="category-card-grid">
          {featured && <CategoryCard category={featured} />}
          {rest.map((category) => (
            <CategoryCard key={category.name} category={category} />
          ))}
        </div>
      </div>
    </section>
  );
}
