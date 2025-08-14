// React import handled by Vite automatically
import { useRef, useCallback, useState, useEffect } from 'react';
import TypingIndicator from './TypingIndicator';
import { MarkdownText } from '../utils/markdownParser.jsx';
import SimpleTypewriter from './SimpleTypewriter.jsx';
import ProductStrip from './ProductStrip.jsx';
import { isProductPayload, parseProductPayload } from '../utils/productUtils.js';

const formatTime = (timestamp) => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  }).format(timestamp);
};

const MessageBubble = ({ message, isLatestBot, onTextUpdate }) => {
  const { text, isUser, isError } = message;
  
  // Check if this is a product recommendation message
  const isProductMessage = !isUser && isProductPayload(text);
  const productPayload = isProductMessage ? parseProductPayload(text) : null;
  
  // Debug logging
  if (!isUser && isLatestBot) {
    console.log('🔍 Latest bot message:', { 
      text: text?.substring(0, 200) + (text?.length > 200 ? '...' : ''), 
      textLength: text?.length,
      isProductMessage, 
      productPayload: productPayload ? 'Valid payload detected' : 'No payload'
    });
  }
  
  if (isUser) {
    // User message with circular bubble
    return (
      <div className="flex justify-end jarir-message-enter w-full">
        <div 
          className="max-w-[80%] px-4 py-3 bg-red-600 text-white rounded-3xl shadow-sm"
          style={{
            wordWrap: 'break-word',
            overflowWrap: 'anywhere',
            boxSizing: 'border-box'
          }}
        >
          <div className="text-base leading-relaxed break-words font-medium" style={{ wordWrap: 'break-word', overflowWrap: 'anywhere' }}>
            <div className="whitespace-pre-wrap">{text}</div>
          </div>
        </div>
      </div>
    );
  }
  
  // AI message without bubble
  return (
    <div className="jarir-message-enter w-full">
      {isError ? (
        <div className="px-4 py-3 bg-red-50 text-red-800 border border-red-200 rounded-lg">
          <div className="text-base leading-relaxed break-words">
            {text}
          </div>
        </div>
      ) : (
        <div className="text-gray-900">
          <div className="text-base leading-relaxed break-words" style={{ wordWrap: 'break-word', overflowWrap: 'anywhere' }}>
            {isProductMessage && productPayload ? (
              <ProductStrip payload={productPayload} />
            ) : isLatestBot && !isProductMessage && text ? (
              <SimpleTypewriter text={text} speed={7} onTextUpdate={onTextUpdate} />
            ) : text ? (
              <MarkdownText>{text}</MarkdownText>
            ) : (
              <div className="text-gray-500 italic">Loading...</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const MessageList = ({ messages, isLoading, messagesEndRef, onScrollStateChange }) => {
  const scrollContainerRef = useRef(null);
  const isUserScrollingRef = useRef(false);
  const scrollTimeoutRef = useRef(null);
  const lastScrollTopRef = useRef(0);
  const [atBottom, setAtBottom] = useState(true);

  // Check if user is at the bottom of the scroll
  const isAtBottom = useCallback(() => {
    const container = scrollContainerRef.current;
    if (!container) return true;
    
    const threshold = 30; // pixels from bottom
    return container.scrollHeight - container.scrollTop - container.clientHeight < threshold;
  }, []);

  // Notify parent if atBottom changes
  useEffect(() => {
    if (onScrollStateChange) onScrollStateChange(atBottom);
  }, [atBottom, onScrollStateChange]);

  // Auto scroll to bottom (used during animation)
  const scrollToBottom = useCallback(() => {
    if (!isUserScrollingRef.current && scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, []);

  // Handle user scroll events
  const handleScroll = useCallback((e) => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const currentScrollTop = container.scrollTop;
    const scrollDirection = currentScrollTop - lastScrollTopRef.current;
    
    // If user scrolled up (negative direction), immediately disable auto-scroll
    if (scrollDirection < 0) {
      isUserScrollingRef.current = true;
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    }
    
    // If user is at bottom, enable auto-scroll
    const nowAtBottom = isAtBottom();
    if (nowAtBottom !== atBottom) setAtBottom(nowAtBottom);
    if (nowAtBottom) {
      isUserScrollingRef.current = false;
    }
    
    lastScrollTopRef.current = currentScrollTop;
    
    // Clear any existing timeout
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }
    
    // Reset user scrolling flag after a delay only if at bottom
    scrollTimeoutRef.current = setTimeout(() => {
      if (isAtBottom()) {
        isUserScrollingRef.current = false;
      }
    }, 500);
  }, [isAtBottom, atBottom]);

  const handleWheel = useCallback((e) => {
    const container = scrollContainerRef.current;
    if (!container) return;

    // If user is wheeling up, immediately disable auto-scroll
    if (e.deltaY < 0) {
      isUserScrollingRef.current = true;
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    }

    e.stopPropagation();
    // Allow scrolling within the message list
    const isScrollable = container.scrollHeight > container.clientHeight;
    if (!isScrollable) {
      e.preventDefault();
    }
  }, []);

  // Find the latest bot message
  const getLatestBotMessageId = () => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (!messages[i].isUser) {
        return messages[i].id;
      }
    }
    return null;
  };

  const latestBotId = getLatestBotMessageId();

  return (
    <div 
      ref={scrollContainerRef}
      className="flex-1 overflow-y-auto overflow-x-hidden px-6 py-4 jarir-scrollbar bg-white min-h-0 w-full"
      onWheel={handleWheel}
      onScroll={handleScroll}
      style={{ 
        scrollbarWidth: 'thin',
        scrollbarColor: '#cbd5e1 #f1f5f9',
        boxSizing: 'border-box'
      }}
    >
      <div className="flex flex-col gap-y-10">
        {messages.map((message) => (
          <MessageBubble 
            key={message.id} 
            message={message}
            isLatestBot={!message.isUser && message.id === latestBotId}
            onTextUpdate={scrollToBottom}
          />
        ))}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <TypingIndicator />
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList; 