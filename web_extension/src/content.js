import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
import ChatWidget from './components/ChatWidget';
import { 
  createHostElement, 
  createShadowRoot, 
  injectStyles, 
  setupMutationObserver 
} from './utils/shadowDom';
import './styles/globals.css';

let root = null;
let observer = null;

// Initialize the chat widget
const initializeChatWidget = () => {
  try {
    // Create host element
    const hostElement = createHostElement('jarir-ai-host');
    
    // Create shadow root
    const shadowRoot = createShadowRoot(hostElement);
    
    // Inject styles - CSS will be automatically injected by Vite
    // We'll use a link element to load the CSS
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = chrome.runtime.getURL('dist/content.css');
    shadowRoot.appendChild(cssLink);
    
    // Create React container
    const reactContainer = document.createElement('div');
    reactContainer.id = 'jarir-chat-root';
    shadowRoot.appendChild(reactContainer);
    
    // Initialize React app
    if (root) {
      root.unmount();
    }
    
    root = createRoot(reactContainer);
    root.render(createElement(ChatWidget));
    
    console.log('✅ Jarir AI Chat Widget initialized');
    
  } catch (error) {
    console.error('❌ Failed to initialize Jarir AI Chat Widget:', error);
  }
};

// Cleanup function
const cleanup = () => {
  if (root) {
    root.unmount();
    root = null;
  }
  
  if (observer) {
    observer.disconnect();
    observer = null;
  }
  
  const hostElement = document.getElementById('jarir-ai-host');
  if (hostElement) {
    hostElement.remove();
  }
};

// Main initialization
const init = () => {
  // Cleanup any existing instances
  cleanup();
  
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChatWidget);
  } else {
    initializeChatWidget();
  }
  
  // Setup mutation observer for SPA navigation
  observer = setupMutationObserver(() => {
    console.log('🔄 SPA navigation detected, reinitializing chat widget...');
    setTimeout(initializeChatWidget, 1000); // Delay to ensure new page is loaded
  });
};

// Handle extension lifecycle
if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.onMessage) {
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'reinitialize') {
      init();
      sendResponse({ status: 'reinitialized' });
    }
  });
}

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    // Check if widget still exists and reinitialize if needed
    setTimeout(() => {
      const hostElement = document.getElementById('jarir-ai-host');
      if (!hostElement) {
        initializeChatWidget();
      }
    }, 500);
  }
});

// Initialize on script load
init();

// Cleanup on page unload
window.addEventListener('beforeunload', cleanup); 