export const createShadowRoot = (hostElement) => {
  if (hostElement.shadowRoot) {
    return hostElement.shadowRoot;
  }
  
  return hostElement.attachShadow({ mode: 'open' });
};

export const injectStyles = (shadowRoot, cssText) => {
  const style = document.createElement('style');
  style.textContent = cssText;
  shadowRoot.appendChild(style);
};

export const setupMutationObserver = (callback) => {
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        // Check if our bubble was removed
        const bubbleExists = document.getElementById('jarir-ai-host');
        if (!bubbleExists) {
          callback();
        }
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  return observer;
};



export const createHostElement = (id = 'jarir-ai-host') => {
  // Remove existing host if it exists
  const existing = document.getElementById(id);
  if (existing) {
    existing.remove();
  }

  const host = document.createElement('div');
  host.id = id;
  host.style.cssText = `
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    pointer-events: none !important;
    z-index: 2147483647 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
  `;
  
  document.body.appendChild(host);
  return host;
}; 