// React import handled by Vite automatically
import { useState, useEffect } from 'react';
import { parseMarkdown } from '../utils/markdownParser.jsx';

const SimpleTypewriter = ({ text, speed = 15, onTextUpdate = () => {} }) => {
  const [displayText, setDisplayText] = useState('');

  useEffect(() => {
    if (!text) return;
    
    setDisplayText('');
    let i = 0;
    
    const timer = setInterval(() => {
      if (i <= text.length) {
        const currentText = text.substring(0, i);
        setDisplayText(currentText);
        // Trigger scroll on each character update
        onTextUpdate();
        i++;
      } else {
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, onTextUpdate]);

  // Parse the displayed text as markdown
  const htmlContent = parseMarkdown(displayText);

  return (
    <div 
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: htmlContent }} 
    />
  );
};

export default SimpleTypewriter; 