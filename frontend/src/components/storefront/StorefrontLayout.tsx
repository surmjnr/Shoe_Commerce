import { ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getStoreSettings } from '@/services/storeApi';
import { Header } from './Header';
import { Footer } from './Footer';

export function StorefrontLayout({ children }: { children: ReactNode }) {
  const settings = useQuery({ queryKey: ['store-settings'], queryFn: getStoreSettings });

  return (
    <div className="shell">
      <Header />
      {children}
      <Footer settings={settings.data} />
    </div>
  );
}
