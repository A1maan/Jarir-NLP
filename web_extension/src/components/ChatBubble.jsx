// React import handled by Vite automatically
import { MessageCircle } from 'lucide-react';

const ChatBubble = ({ onClick, isOpen }) => {
  return (
    <button
      onClick={onClick}
      className={`
        fixed bottom-6 right-6 w-16 h-16 text-white rounded-full 
        transition-all duration-300 focus:outline-none focus:ring-4 
        focus:ring-blue-200/50 z-50 group backdrop-blur-sm
        ${isOpen ? 'scale-110' : 'jarir-bubble-pulse hover:scale-105'}
      `}
      style={{ 
        pointerEvents: 'auto',
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.9) 0%, rgba(99, 102, 241, 0.9) 50%, rgba(139, 92, 246, 0.9) 100%)',
        backdropFilter: 'blur(10px) saturate(180%)',
        boxShadow: '0 20px 25px -5px rgba(59, 130, 246, 0.4), 0 10px 10px -5px rgba(59, 130, 246, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.1)',
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