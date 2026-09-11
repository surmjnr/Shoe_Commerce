import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getProductFilterOptions, getProducts } from '@/services/storeApi';
import type { Product } from '@/types';
import type { FilterOption } from '@/services/storeApi';
import { HeroSection } from './HeroSection';
import { CategorySection } from './CategorySection';
import type { CategoryWithImage } from './CategoryCard';
import { ProductSection } from './ProductSection';
import { PromoBanner } from './PromoBanner';
import { TrustSection } from './TrustSection';

function buildCategories(categories: FilterOption[], products: Product[]): CategoryWithImage[] {
  const fromApi = categories.length
    ? categories.map((entry) => entry.name || entry.value || '').filter(Boolean)
    : [...new Set(products.map((product) => product.category).filter(Boolean))];

  return fromApi.map((name) => {
    const categoryProducts = products.filter((product) => product.category === name);
    const withImage = categoryProducts.find((product) => product.primary_image_url);
    return {
      name,
      imageUrl: withImage?.primary_image_url || null,
      productCount: categoryProducts.length,
    };
  });
}

function pickFeaturedProduct(featured: Product[] | undefined, all: Product[] | undefined) {
  const featuredWithImage = featured?.find((product) => product.primary_image_url);
  if (featuredWithImage) return featuredWithImage;
  return all?.find((product) => product.primary_image_url) || featured?.[0] || all?.[0] || null;
}

export function Home() {
  const products = useQuery({ queryKey: ['products', 'home'], queryFn: () => getProducts() });
  const featuredProducts = useQuery({
    queryKey: ['products', 'featured'],
    queryFn: () => getProducts({ featured: true }),
  });
  const filterOptions = useQuery({ queryKey: ['product-filter-options'], queryFn: getProductFilterOptions });

  const categories = useMemo(
    () => buildCategories(filterOptions.data?.categories || [], products.data || []),
    [filterOptions.data?.categories, products.data],
  );

  const featuredProduct = useMemo(
    () => pickFeaturedProduct(featuredProducts.data, products.data),
    [featuredProducts.data, products.data],
  );

  const loading = products.isLoading || featuredProducts.isLoading;

  return (
    <main className="container home-page">
      <HeroSection featuredProduct={featuredProduct} loading={loading} />
      <CategorySection categories={categories} loading={filterOptions.isLoading || products.isLoading} />
      <ProductSection
        eyebrow="Just in"
        title="New arrivals"
        subtitle="Fresh styles added to the collection"
        linkTo="/products?featured=true"
        filters={{ featured: true }}
        limit={4}
      />
      <PromoBanner />
      <ProductSection
        eyebrow="Customer favorites"
        title="Best sellers"
        subtitle="Popular pairs our shoppers love"
        linkTo="/products"
        limit={4}
      />
      <TrustSection />
    </main>
  );
}
