// React import handled by Vite automatically
import { ExternalLink } from 'lucide-react';

const ProductCard = ({ item }) => {
  const { id, name, image, priceSar, url, badges = [], description } = item;

  const handleClick = () => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  // Extract key specs from name or description
  const extractSpecs = (name, description) => {
    const specs = [];
    const text = `${name} ${description || ''}`.toLowerCase();
    
    // Extract RAM
    const ramMatch = text.match(/(\d+gb)\s*ram/i);
    if (ramMatch) specs.push(`${ramMatch[1]} RAM`);
    
    // Extract Storage
    const storageMatch = text.match(/(\d+gb|\d+tb)\s*(ssd|storage)/i);
    if (storageMatch) specs.push(`${storageMatch[1]} ${storageMatch[2].toUpperCase()}`);
    
    // Extract Screen Size
    const screenMatch = text.match(/(\d+\.?\d*)["\s]*inch|\s(\d+\.?\d*)"|\s(\d+\.?\d*)\s*inch/i);
    if (screenMatch) {
      const size = screenMatch[1] || screenMatch[2] || screenMatch[3];
      specs.push(`${size}" Display`);
    }
    
    // Extract Chip/Processor
    const chipMatch = text.match(/(m[1-4]\s*(?:pro|max|ultra)?|intel|amd)/i);
    if (chipMatch) specs.push(chipMatch[1].toUpperCase());
    
    return specs.slice(0, 4); // Limit to 4 specs
  };

  const specs = extractSpecs(name, description);

  return (
    <div className="w-72 shrink-0 bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-200 hover:shadow-xl transition-all duration-300 hover:scale-105">
      {/* Product Image */}
      <div className="relative h-40 overflow-hidden bg-gray-50 flex items-center justify-center">
        <img
          src={image}
          alt={name}
          className="max-w-full max-h-full object-contain"
          onError={(e) => {
            e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjg4IiBoZWlnaHQ9IjE2MCIgdmlld0JveD0iMCAwIDI4OCAxNjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyODgiIGhlaWdodD0iMTYwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xNDQgODBMMTYwIDk2SDE2MFY5NkgxNjhWOTZMMTQ0IDgwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K';
          }}
        />
        {badges.length > 0 && (
          <div className="absolute top-3 left-3 flex flex-wrap gap-1">
            {badges.map((badge, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs font-medium bg-red-600 text-white rounded-full shadow-sm"
              >
                {badge}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Product Details */}
      <div className="p-5 space-y-4">
        <h3 className="text-base font-semibold leading-tight text-gray-900 line-clamp-2">
          {name}
        </h3>
        
        {/* Specs */}
        {specs.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {specs.map((spec, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-md"
              >
                {spec}
              </span>
            ))}
          </div>
        )}
        
        <div className="flex items-center justify-between pt-2">
          <div className="flex flex-col">
            <span className="text-xl font-bold text-gray-900">
              {priceSar.toLocaleString()} SAR
            </span>
          </div>
          
          <button
            onClick={handleClick}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors duration-200 shadow-sm"
            title="View Product"
          >
            <ExternalLink className="w-4 h-4" />
            View
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;