// React import handled by Vite automatically
import TypingIndicator from './TypingIndicator';
import { MarkdownText } from '../utils/markdownParser.jsx';

const formatTime = (timestamp) => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  }).format(timestamp);
};

const MessageBubble = ({ message }) => {
  const { text, isUser, timestamp, isError } = message;
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 jarir-message-enter w-full max-w-full`}>
      <div 
        className={`max-w-[320px] px-4 py-3 rounded-lg ${
          isUser 
            ? 'bg-jarir-blue text-white' 
            : isError
              ? 'bg-red-100 text-red-800 border border-red-200'
              : 'bg-gray-100 text-gray-800'
        } shadow-sm`}
        style={{
          maxWidth: '320px',
          wordWrap: 'break-word',
          overflowWrap: 'anywhere',
          boxSizing: 'border-box'
        }}
      >
        <div className="text-base leading-relaxed break-words word-wrap overflow-wrap-anywhere" style={{ maxWidth: '100%', wordWrap: 'break-word', overflowWrap: 'anywhere' }}>
          {isUser ? (
            <div className="whitespace-pre-wrap">{text}</div>
          ) : (
            <MarkdownText>{text}</MarkdownText>
          )}
        </div>
        <div className={`text-xs mt-2 opacity-70 ${isUser ? 'text-right' : 'text-left'}`}>
          {formatTime(timestamp)}
        </div>
      </div>
    </div>
  );
};

const MessageList = ({ messages, isLoading, messagesEndRef }) => {
  const handleWheel = (e) => {
    e.stopPropagation();
    // Allow scrolling within the message list
    const element = e.currentTarget;
    const isScrollable = element.scrollHeight > element.clientHeight;
    if (!isScrollable) {
      e.preventDefault();
    }
  };

  return (
    <div 
      className="flex-1 overflow-y-auto overflow-x-hidden p-4 jarir-scrollbar bg-gray-50 min-h-0 w-full max-w-full"
      onWheel={handleWheel}
      style={{ 
        scrollbarWidth: 'thin',
        scrollbarColor: '#cbd5e1 #f1f5f9',
        width: '100%',
        maxWidth: '480px',
        boxSizing: 'border-box'
      }}
    >
      <div className="space-y-1">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
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