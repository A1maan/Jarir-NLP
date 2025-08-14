// React import handled by Vite automatically
import { MessageCircle } from 'lucide-react';

const ChatBubble = ({ onClick, isOpen }) => {
  return (
    <button
      onClick={onClick}
      className={`
        fixed bottom-6 right-6 w-16 h-16 text-white rounded-full 
        transition-all duration-300 focus:outline-none focus:ring-4 
        focus:ring-red-200/50 z-50 group
        ${isOpen ? 'scale-110' : 'jarir-bubble-pulse hover:scale-105'}
      `}
      style={{ 
        pointerEvents: 'auto',
        background: 'linear-gradient(135deg, rgba(237, 28, 36, 1) 0%, rgba(220, 20, 30, 1) 50%, rgba(200, 15, 25, 1) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.2)'
      }}
      title="Open Jarir AI Assistant"
    >
      <div className="flex items-center justify-center w-full h-full">
        <MessageCircle 
          className={`w-7 h-7 transition-transform duration-300 ${
            isOpen ? 'rotate-12' : 'group-hover:scale-110'
          }`} 
        />
      </div>
      
      {/* Notification badge (optional for future use) */}
      {false && (
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
          <span className="text-xs font-bold text-gray-800">!</span>
        </div>
      )}
    </button>
  );
};

export default ChatBubble; 