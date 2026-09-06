import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CartItem } from '@/types';

type CartState = {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  updateQuantity: (variantId: number, quantity: number) => void;
  removeItem: (variantId: number) => void;
  clear: () => void;
};

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      addItem: (item) =>
        set((state) => {
          const existing = state.items.find((entry) => entry.variantId === item.variantId);
          if (existing) {
            return {
              items: state.items.map((entry) =>
                entry.variantId === item.variantId
                  ? { ...entry, quantity: Math.min(entry.quantity + item.quantity, entry.maxStock) }
                  : entry,
              ),
            };
          }
          return { items: [...state.items, item] };
        }),
      updateQuantity: (variantId, quantity) =>
        set((state) => ({
          items: state.items.map((item) =>
            item.variantId === variantId
              ? { ...item, quantity: Math.max(1, Math.min(quantity, item.maxStock)) }
              : item,
          ),
        })),
      removeItem: (variantId) =>
        set((state) => ({ items: state.items.filter((item) => item.variantId !== variantId) })),
      clear: () => set({ items: [] }),
    }),
    { name: 'shoe-store-cart' },
  ),
);
