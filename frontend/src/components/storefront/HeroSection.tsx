import { Link } from 'react-router-dom';
import type { Product } from '@/types';
import { FeaturedProductShowcase } from './FeaturedProductShowcase';

type HeroSectionProps = {
  featuredProduct?: Product | null;
  loading?: boolean;
};

export function HeroSection({ featuredProduct, loading }: HeroSectionProps) {
  return (
    <section className="hero">
      <div className="hero__content">
        <span className="eyebrow">Premium footwear · Curated daily</span>
        <h1 className="display hero__title">Step into style that moves with you.</h1>
        <p className="hero-copy">
          Discover thoughtfully selected shoes for every moment — from everyday casual to statement formal. Quality pairs,
          delivered with care.
        </p>
        <div className="hero-actions">
          <Link className="button" to="/products">
            Shop collection
          </Link>
          <Link className="button secondary" to="/products">
            Browse the collection
          </Link>
        </div>
        <p className="hero-trust">
          <span>Free local delivery guidance</span>
          <span aria-hidden="true">·</span>
          <span>Pay on delivery available</span>
        </p>
      </div>

      <FeaturedProductShowcase product={featuredProduct} loading={loading} />
    </section>
  );
}
