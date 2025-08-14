/**
 * Checks if a message contains product recommendation JSON
 * @param {string} text - The message text to check
 * @returns {boolean} - True if the text contains product recommendations
 */
export function isProductPayload(text) {
  try {
    // Check if text exists and is not empty
    if (!text || typeof text !== 'string' || !text.trim()) {
      return false;
    }

    const trimmedText = text.trim();
    
    // Look for JSON blocks anywhere in the text (markdown format)
    const jsonMatch = trimmedText.match(/```json\s*([\s\S]*?)\s*```/);
    
    let jsonText;
    let parsed;
    
    if (jsonMatch) {
      // Extract and parse JSON from markdown block
      jsonText = jsonMatch[1].trim();
      parsed = JSON.parse(jsonText);
      console.log('✅ Found JSON in markdown block');
    } else if (trimmedText.startsWith('{') || trimmedText.startsWith('`json\n{')) {
      // Handle raw JSON or `json format (without triple backticks)
      if (trimmedText.startsWith('`json\n')) {
        // Extract JSON from `json format
        jsonText = trimmedText.replace(/^`json\s*/, '').trim();
      } else {
        // Raw JSON
        jsonText = trimmedText;
      }
      parsed = JSON.parse(jsonText);
      console.log('✅ Found raw JSON or `json format');
    } else {
      return false;
    }
    
    const isValid = parsed?.type === 'product_recommendations' && Array.isArray(parsed?.items) && parsed.items.length > 0;
    
    // Debug logging
    if (isValid) {
      console.log('✅ Product payload detected (markdown block):', { 
        heading: parsed.heading, 
        itemCount: parsed.items.length,
        firstItem: parsed.items[0]?.name 
      });
    } else {
      console.log('❌ Invalid product payload:', { type: parsed?.type, hasItems: Array.isArray(parsed?.items) });
    }
    
    return isValid;
  } catch (error) {
    console.log('❌ Failed to parse as product payload:', error.message, 'Text preview:', text?.substring(0, 100));
    return false;
  }
}

/**
 * Parses product recommendation JSON from message text
 * @param {string} text - The message text containing JSON
 * @returns {Object|null} - Parsed product payload or null if invalid
 */
export function parseProductPayload(text) {
  try {
    if (!text || typeof text !== 'string' || !text.trim()) {
      return null;
    }

    const trimmedText = text.trim();
    
    // Look for JSON blocks anywhere in the text
    const jsonMatch = trimmedText.match(/```json\s*([\s\S]*?)\s*```/);
    
    let jsonText;
    if (jsonMatch) {
      // Extract from markdown block
      jsonText = jsonMatch[1].trim();
    } else if (trimmedText.startsWith('{') || trimmedText.startsWith('`json\n{')) {
      // Handle raw JSON or `json format (without triple backticks)
      if (trimmedText.startsWith('`json\n')) {
        // Extract JSON from `json format
        jsonText = trimmedText.replace(/^`json\s*/, '').trim();
      } else {
        // Raw JSON
        jsonText = trimmedText;
      }
    } else {
      return null;
    }
    
    const parsed = JSON.parse(jsonText);
    
    if (parsed?.type === 'product_recommendations' && Array.isArray(parsed?.items)) {
      return parsed;
    }
    
    return null;
  } catch (error) {
    console.warn('Failed to parse product payload:', error);
    return null;
  }
}