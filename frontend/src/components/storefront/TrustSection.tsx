import { useQuery } from '@tanstack/react-query';
import { getStoreSettings } from '@/services/storeApi';

const benefits = [
  {
    title: 'Curated selection',
    text: 'Every pair is chosen for quality, comfort, and everyday wearability.',
  },
  {
    title: 'Flexible payment',
    text: 'Pay on delivery or Mobile Money — checkout options that work for you.',
  },
  {
    title: 'Local delivery',
    text: 'Reliable delivery with clear updates from order to doorstep.',
  },
  {
    title: 'Order tracking',
    text: 'Follow your purchase every step of the way with our track tool.',
  },
];

export function TrustSection() {
  const settings = useQuery({ queryKey: ['store-settings'], queryFn: getStoreSettings });

  return (
    <section className="section trust-section">
      <div className="trust-section__intro">
        <div className="eyebrow">Why shop with us</div>
        <h2>Shopping made simple</h2>
        {settings.data?.description && <p className="section-subtitle">{settings.data.description}</p>}
      </div>
      <div className="trust-grid">
        {benefits.map((benefit) => (
          <article key={benefit.title} className="trust-card">
            <h3>{benefit.title}</h3>
            <p>{benefit.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
