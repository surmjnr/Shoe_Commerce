import { useQuery } from '@tanstack/react-query';
import { getProducts, type ProductFilters } from '@/services/storeApi';
import { ProductCard } from './ProductCard';

type ProductGridProps = {
  filters?: ProductFilters;
  search?: string;
  limit?: number;
};

export function ProductGrid({ filters = {}, search = '', limit }: ProductGridProps) {
  const query = useQuery({
    queryKey: ['products', { ...filters, search }],
    queryFn: () => getProducts({ ...filters, search }),
  });

  if (query.isLoading) {
    return <div className="state">Loading the collection...</div>;
  }

  if (query.isError) {
    return <div className="state">We could not load the collection. Please try again.</div>;
  }

  const products = limit ? query.data?.slice(0, limit) : query.data;

  if (!products?.length) {
    return (
      <div className="state">
        No shoes match the selected filters. Try adjusting your search or resetting the filters.
      </div>
    );
  }

  return (
    <div className="grid">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
