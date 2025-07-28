import { useState, useRef, useEffect, useCallback } from 'react';
import { X, Minimize2, RotateCcw } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { useDraggable } from '../hooks/useDraggable'; // Import the new hook
import ChatBubble from './ChatBubble';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  
  const dragRef = useRef(null);
  const { position, onMouseDown } = useDraggable(dragRef); // Use the hook

  const {
    messages,
    isLoading,
    inputValue,
    setInputValue,
    sendMessage,
    clearMessages,
    messagesEndRef
  } = useChat();

  const toggleChat = () => {
    if (!isOpen) {
      setIsOpen(true);
      setIsMinimized(false);
    } else {
      setIsOpen(false);
      setIsMinimized(false);
    }
  };

  const handleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleSend = () => {
    sendMessage(inputValue);
  };

  if (!isOpen) {
    return <ChatBubble onClick={toggleChat} isOpen={isOpen} />;
  }

  return (
    <>
      <ChatBubble onClick={toggleChat} isOpen={isOpen} />
      
      <div
        ref={dragRef}
        className={`
          fixed w-[480px] max-w-[480px] min-w-[480px] bg-white border border-gray-200 rounded-xl 
          shadow-2xl overflow-hidden transition-all duration-300 z-40
          ${isMinimized ? 'h-16' : 'h-[600px]'}
        `}
        style={{
          position: 'fixed',
          right: position.x === 0 && position.y === 0 ? '24px' : 'auto',
          bottom: position.x === 0 && position.y === 0 ? '100px' : 'auto',
          left: position.x !== 0 || position.y !== 0 ? `${position.x}px` : 'auto',
          top: position.x !== 0 || position.y !== 0 ? `${position.y}px` : 'auto',
          pointerEvents: 'auto',
          zIndex: 9999,
          width: '480px',
          maxWidth: '480px',
          minWidth: '480px',
          boxSizing: 'border-box'
        }}
      >
        {/* Header - Draggable */}
        <div
          className="flex items-center justify-between p-3 bg-gradient-to-r from-jarir-red to-red-600 text-white cursor-grab active:cursor-grabbing"
          onMouseDown={onMouseDown}
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold">🤖</span>
            </div>
            <div>
              <h3 className="font-semibold text-base">Jarir AI Assistant</h3>
              <p className="text-sm opacity-90">Connected</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={clearMessages}
              className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
              title="Clear Chat"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            
            <button
              onClick={handleMinimize}
              className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
              title={isMinimized ? "Expand" : "Minimize"}
            >
              <Minimize2 className="w-4 h-4" />
            </button>
            
            <button
              onClick={toggleChat}
              className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Chat Content */}
        {!isMinimized && (
          <div 
            className="flex flex-col w-full max-w-full overflow-hidden" 
            style={{ 
              height: 'calc(600px - 64px)',
              width: '480px',
              maxWidth: '480px',
              boxSizing: 'border-box'
            }}
          >
            <MessageList 
              messages={messages}
              isLoading={isLoading}
              messagesEndRef={messagesEndRef}
            />
            
            <MessageInput
              value={inputValue}
              onChange={setInputValue}
              onSend={handleSend}
              disabled={isLoading}
              placeholder="Ask about Jarir products..."
            />
          </div>
        )}
      </div>
    </>
  );
};

export default ChatWidget; 