// Simple markdown parser for basic formatting
export const parseMarkdown = (text) => {
  if (!text) return '';
  
  // Split text into paragraphs and process each one
  const paragraphs = text.split(/\n\s*\n/);
  
  return paragraphs.map(paragraph => {
    // Process bold text (**text** or __text__)
    let processed = paragraph.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    processed = processed.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // Process italic text (*text* or _text_)
    processed = processed.replace(/\*(.*?)\*/g, '<em>$1</em>');
    processed = processed.replace(/_(.*?)_/g, '<em>$1</em>');
    
    // Process inline code (`code`)
    processed = processed.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Convert line breaks within paragraphs to <br>
    processed = processed.replace(/\n/g, '<br>');
    
    return `<p>${processed}</p>`;
  }).join('');
};

// React component for rendering markdown
export const MarkdownText = ({ children, className = '' }) => {
  const htmlContent = parseMarkdown(children);
  
  return (
    <div 
      className={`markdown-content ${className}`}
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
}; 