// React import handled by Vite automatically
import ProductCard from './ProductCard';

const ProductStrip = ({ payload }) => {
  const { heading, items } = payload;

  if (!items || items.length === 0) {
    return null;
  }

  return (
    <section className="flex flex-col gap-4 w-full">
      {heading && (
        <h4 className="font-semibold text-gray-900 text-base leading-tight">
          {heading}
        </h4>
      )}
      
      <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
        {items.map((item) => (
          <ProductCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
};

export default ProductStrip;