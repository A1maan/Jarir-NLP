import { useState, useRef, useEffect, useCallback } from 'react';
import { X, RotateCcw } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { useDraggable } from '../hooks/useDraggable';
import ChatBubble from './ChatBubble';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [dimensions, setDimensions] = useState({ width: 480, height: 600 });
  const [isResizing, setIsResizing] = useState(false);
  const [resizeHandle, setResizeHandle] = useState(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  
  const dragRef = useRef(null);
  const resizeRef = useRef(null);
  const { position, onMouseDown } = useDraggable(dragRef);

  const {
    messages,
    isLoading,
    inputValue,
    setInputValue,
    sendMessage,
    clearMessages,
    messagesEndRef
  } = useChat();

  // Resize functionality
  const handleResizeStart = useCallback((e, handle) => {
    e.preventDefault();
    e.stopPropagation();
    setIsResizing(true);
    setResizeHandle(handle);
    
    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = dimensions.width;
    const startHeight = dimensions.height;

    const handleMouseMove = (e) => {
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;
      
      let newWidth = startWidth;
      let newHeight = startHeight;

      // Handle different resize directions
      if (handle.includes('right')) {
        newWidth = Math.max(320, Math.min(800, startWidth + deltaX));
      }
      if (handle.includes('left')) {
        newWidth = Math.max(320, Math.min(800, startWidth - deltaX));
      }
      if (handle.includes('bottom')) {
        newHeight = Math.max(400, Math.min(800, startHeight + deltaY));
      }
      if (handle.includes('top')) {
        newHeight = Math.max(400, Math.min(800, startHeight - deltaY));
      }

      setDimensions({ width: newWidth, height: newHeight });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      setResizeHandle(null);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [dimensions]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
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
          fixed bg-white border border-gray-200 rounded-xl 
          shadow-2xl overflow-hidden transition-all duration-300
          ${isResizing ? 'select-none' : ''}
        `}
        style={{
          left: position.x || (window.innerWidth - dimensions.width - 24),
          top: position.y || 100,
          zIndex: 2147483647, // Maximum z-index value
          width: dimensions.width,
          height: dimensions.height,
          minWidth: 320,
          maxWidth: 800,
          minHeight: 400,
          maxHeight: 800,
          boxSizing: 'border-box',
          pointerEvents: 'auto',
          position: 'fixed'
        }}
      >
        {/* Resize Handles */}
        <>
            {/* Corner handles */}
            <div
              className="absolute top-0 right-0 w-3 h-3 cursor-nw-resize opacity-0 hover:opacity-100 transition-opacity z-10"
              style={{ 
                background: 'linear-gradient(-45deg, transparent 30%, #666 30%, #666 70%, transparent 70%)',
                pointerEvents: 'auto'
              }}
              onMouseDown={(e) => handleResizeStart(e, 'top-right')}
            />
            <div
              className="absolute bottom-0 right-0 w-3 h-3 cursor-nw-resize opacity-0 hover:opacity-100 transition-opacity z-10"
              style={{ 
                background: 'linear-gradient(45deg, transparent 30%, #666 30%, #666 70%, transparent 70%)',
                pointerEvents: 'auto'
              }}
              onMouseDown={(e) => handleResizeStart(e, 'bottom-right')}
            />
            <div
              className="absolute bottom-0 left-0 w-3 h-3 cursor-ne-resize opacity-0 hover:opacity-100 transition-opacity z-10"
              style={{ 
                background: 'linear-gradient(-45deg, transparent 30%, #666 30%, #666 70%, transparent 70%)',
                pointerEvents: 'auto'
              }}
              onMouseDown={(e) => handleResizeStart(e, 'bottom-left')}
            />
            <div
              className="absolute top-0 left-0 w-3 h-3 cursor-ne-resize opacity-0 hover:opacity-100 transition-opacity z-10"
              style={{ 
                background: 'linear-gradient(45deg, transparent 30%, #666 30%, #666 70%, transparent 70%)',
                pointerEvents: 'auto'
              }}
              onMouseDown={(e) => handleResizeStart(e, 'top-left')}
            />

            {/* Edge handles */}
            <div
              className="absolute top-0 left-3 right-3 h-1 cursor-n-resize opacity-0 hover:opacity-100 hover:bg-gray-400 transition-all z-10"
              style={{ pointerEvents: 'auto' }}
              onMouseDown={(e) => handleResizeStart(e, 'top')}
            />
            <div
              className="absolute bottom-0 left-3 right-3 h-1 cursor-n-resize opacity-0 hover:opacity-100 hover:bg-gray-400 transition-all z-10"
              style={{ pointerEvents: 'auto' }}
              onMouseDown={(e) => handleResizeStart(e, 'bottom')}
            />
            <div
              className="absolute left-0 top-3 bottom-3 w-1 cursor-e-resize opacity-0 hover:opacity-100 hover:bg-gray-400 transition-all z-10"
              style={{ pointerEvents: 'auto' }}
              onMouseDown={(e) => handleResizeStart(e, 'left')}
            />
            <div
              className="absolute right-0 top-3 bottom-3 w-1 cursor-e-resize opacity-0 hover:opacity-100 hover:bg-gray-400 transition-all z-10"
              style={{ pointerEvents: 'auto' }}
              onMouseDown={(e) => handleResizeStart(e, 'right')}
            />
        </>

        {/* Header - Draggable */}
        <div
          className="flex items-center justify-between p-3 bg-gradient-to-r from-jarir-red to-red-600 text-white cursor-grab active:cursor-grabbing relative z-20"
          style={{ pointerEvents: 'auto' }}
          onMouseDown={onMouseDown}
        >
          <div className="flex items-center">
            <h3 className="font-semibold text-lg">Jarir AI Assistant</h3>
          </div>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={clearMessages}
              className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
              title="Clear Chat"
              style={{ pointerEvents: 'auto' }}
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            
            <button
              onClick={toggleChat}
              className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
              title="Close"
              style={{ pointerEvents: 'auto' }}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Chat Content */}
        <div 
          className="flex flex-col w-full max-w-full overflow-hidden relative z-10" 
          style={{ 
            height: dimensions.height - 64,
            width: dimensions.width,
            maxWidth: dimensions.width,
            boxSizing: 'border-box',
            pointerEvents: 'auto'
          }}
        >
          <MessageList 
            messages={messages}
            isLoading={isLoading}
            messagesEndRef={messagesEndRef}
            onScrollStateChange={setIsAtBottom}
          />

          {/* Fade overlay above input, only when not at bottom */}
          {!isAtBottom && (
            <div
              className="pointer-events-none absolute left-0 right-0 bottom-[64px] h-12 z-20 backdrop-blur-md"
              style={{
                background: "rgba(255,255,255,0.6)"
              }}
            />
          )}
          
          <MessageInput
            value={inputValue}
            onChange={setInputValue}
            onSend={handleSend}
            disabled={isLoading}
            placeholder="Ask about Jarir products..."
          />
        </div>
      </div>
    </>
  );
};

export default ChatWidget; 