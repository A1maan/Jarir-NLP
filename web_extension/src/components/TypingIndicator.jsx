// React import handled by Vite automatically

const TypingIndicator = () => {
  return (
    <div 
      className="flex items-center space-x-2 px-5 py-4 rounded-3xl max-w-xs animate-fade-in backdrop-blur-sm border border-white/20"
      style={{
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(255, 255, 255, 0.2)'
      }}
    >
      <div className="flex space-x-1">
        <div className="w-2.5 h-2.5 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full jarir-typing-dot"></div>
        <div className="w-2.5 h-2.5 bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-full jarir-typing-dot"></div>
        <div className="w-2.5 h-2.5 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full jarir-typing-dot"></div>
      </div>
      <span className="text-sm text-gray-600 font-medium">AI is thinking...</span>
    </div>
  );
};

export default TypingIndicator; 