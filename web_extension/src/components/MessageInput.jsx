// React import handled by Vite automatically
import { Send, Loader2 } from 'lucide-react';

const MessageInput = ({ 
  value, 
  onChange, 
  onSend, 
  disabled, 
  placeholder = "Type your message here..."
}) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSend();
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className="flex items-start gap-2 p-3 border-t border-gray-200 bg-white flex-shrink-0"
      onWheel={(e) => e.stopPropagation()}
    >
      <div className="flex-1">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="w-full px-4 py-3 text-base border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-jarir-blue focus:border-transparent transition-all duration-200 disabled:bg-gray-50 disabled:cursor-not-allowed bg-white text-gray-900 placeholder-gray-500"
          style={{
            maxHeight: '120px',
            minHeight: '48px',
            lineHeight: '1.5'
          }}
          onInput={(e) => {
            e.target.style.height = 'auto';
            e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
          }}
          onWheel={(e) => e.stopPropagation()}
        />
      </div>
      
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="flex items-center justify-center w-12 h-12 bg-jarir-blue hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-jarir-blue focus:ring-offset-2 mt-0.5 flex-shrink-0"
      >
        {disabled ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Send className="w-4 h-4" />
        )}
      </button>
    </form>
  );
};

export default MessageInput; 