// React import handled by Vite automatically
import { useState, useEffect } from 'react';
import { MarkdownText } from '../utils/markdownParser.jsx';

const TypewriterText = ({ 
  text, 
  speed = 30, 
  className = '', 
  isMarkdown = false,
  onComplete = () => {} 
}) => {
  const [displayedText, setDisplayedText] = useState('');
  
  useEffect(() => {
    if (!text) {
      setDisplayedText('');
      return;
    }

    let index = 0;
    setDisplayedText('');
    
    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(text.slice(0, index + 1));
        index++;
      } else {
        clearInterval(timer);
        onComplete();
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, onComplete]);

  if (isMarkdown) {
    return (
      <div className={className}>
        <MarkdownText>{displayedText}</MarkdownText>
      </div>
    );
  }

  return (
    <div className={`whitespace-pre-wrap ${className}`}>
      {displayedText}
    </div>
  );
};

export default TypewriterText; 