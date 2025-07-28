import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const injectCSSIntoJS = () => {
  const cssPath = resolve(__dirname, 'dist/content.css');
  const jsPath = resolve(__dirname, 'dist/content.js');
  
  if (!existsSync(cssPath) || !existsSync(jsPath)) {
    console.log('⚠️ CSS or JS file not found, skipping CSS injection');
    return;
  }
  
  const cssContent = readFileSync(cssPath, 'utf-8');
  const jsContent = readFileSync(jsPath, 'utf-8');
  
  // Escape CSS content for injection
  const escapedCSS = cssContent
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$/g, '\\$');
  
  // Create the CSS injection code
  const cssInjectionCode = `
const injectCSS = (shadowRoot, cssText) => {
  const style = document.createElement('style');
  style.textContent = cssText;
  shadowRoot.appendChild(style);
};

const globalStyles = \`${escapedCSS}\`;
`;
  
  // Replace the CSS loading logic with inline CSS
  const modifiedJS = jsContent
    .replace(
      `import './styles/globals.css';`,
      cssInjectionCode
    )
    .replace(
      `// Inject styles - CSS will be automatically injected by Vite
    // We'll use a link element to load the CSS
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = chrome.runtime.getURL('dist/content.css');
    shadowRoot.appendChild(cssLink);`,
      `// Inject styles
    injectCSS(shadowRoot, globalStyles);`
    );
  
  writeFileSync(jsPath, modifiedJS);
  console.log('✅ CSS successfully injected into JS bundle');
};

// Run the CSS injection
injectCSSIntoJS(); 