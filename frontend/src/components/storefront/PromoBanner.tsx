import { Link } from 'react-router-dom';

export function PromoBanner() {
  return (
    <section className="promo-banner" aria-label="Featured collection promotion">
      <div className="promo-banner__inner">
        <div className="promo-banner__copy">
          <span className="eyebrow">Limited collection</span>
          <h2 className="promo-banner__title">Weekend edit — pairs worth the spotlight</h2>
          <p className="promo-banner__text">
            Handpicked styles for your next outing. Explore featured footwear curated for comfort and confidence.
          </p>
          <Link className="button promo-banner__cta" to="/products?featured=true">
            Shop featured
          </Link>
        </div>
        <div className="promo-banner__accent" aria-hidden="true">
          <span>Featured</span>
          <strong>Collection</strong>
        </div>
      </div>
    </section>
  );
}
