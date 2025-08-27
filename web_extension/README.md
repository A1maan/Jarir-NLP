# Jarir AI Chrome/Firefox Extension

A modern, polished browser extension that adds an intelligent AI assistant to Jarir.com pages. Built with React, Tailwind CSS, and Shadow DOM for maximum compatibility and visual polish.

## ✨ Features

- **Modern UI**: Clean, responsive design with Jarir brand colors and smooth animations
- **Shadow DOM Isolation**: Prevents CSS conflicts with the host website
- **Draggable Chat Panel**: Move the chat window anywhere on the page
- **Dark/Light Theme**: Automatic system theme detection with manual toggle
- **Real-time Chat**: Seamless communication with the Jarir AI backend
- **SPA Navigation Resilience**: Automatically reinitializes on page changes
- **Typing Indicators**: Visual feedback during AI response generation
- **Message Timestamps**: Arabic-formatted timestamps for all messages
- **Auto-scroll**: Automatically scrolls to new messages
- **Error Handling**: Graceful error handling with user-friendly messages

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Chrome/Firefox browser for testing
- Jarir AI backend running on `http://127.0.0.1:8000`

### Installation & Build

```bash
# Install dependencies
npm install

# Development build with watch mode
npm run dev

# Production build
npm run build
```

### Loading the Extension

#### Chrome
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `jarir-ai-extension` folder

#### Firefox
1. Open `about:debugging`
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select `manifest.json` from the extension folder

## 🏗️ Project Structure

```
jarir-ai-extension/
├── src/
│   ├── components/
│   │   ├── ChatWidget.jsx      # Main chat component
│   │   ├── ChatBubble.jsx      # Floating action button
│   │   ├── MessageList.jsx     # Message display
│   │   ├── MessageInput.jsx    # Input field with send button
│   │   └── TypingIndicator.jsx # Animated typing dots
│   ├── hooks/
│   │   └── useChat.js          # Chat logic and API calls
│   ├── styles/
│   │   └── globals.css         # Tailwind CSS with custom styles
│   ├── utils/
│   │   └── shadowDom.js        # Shadow DOM utilities
│   └── content.js              # Extension entry point
├── dist/                       # Built files (generated)
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── manifest.json
```

## 🛠️ Development

### File Watching
```bash
npm run dev
# Builds and watches for changes automatically
```

### Production Build
```bash
npm run build
# Creates optimized bundle in dist/
```

### Debugging
- Use Chrome DevTools on the extension popup
- Check console in the webpage where extension is injected
- Inspect Shadow DOM elements for styling issues

## ⚙️ Configuration

### Backend Endpoint
The extension connects to the Jarir AI backend at:
```javascript
// In src/hooks/useChat.js
const response = await fetch('http://127.0.0.1:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: text.trim(),
    context: {} // For future product scraping features
  })
});
```

### Brand Colors
Configured in `tailwind.config.js`:
```javascript
colors: {
  jarir: {
    red: '#ED1C24',    // Primary Jarir red
    blue: '#2563eb',   // Secondary blue
    // ... gray scale variations
  }
}
```

## 🎨 Customization

### Styling
- All styles use Tailwind CSS classes
- Custom animations defined in `tailwind.config.js`
- Shadow DOM prevents CSS conflicts

### Themes
- Automatic system theme detection
- Manual theme toggle in chat header
- Dark mode styles in `globals.css`

### Animations
- Smooth transitions on all interactions
- Typing indicator with staggered dots
- Message entrance animations
- Floating bubble pulse effect

## 🔧 Troubleshooting

### Extension Not Loading
1. Check console for build errors
2. Ensure `dist/` folder exists with built files
3. Verify manifest.json permissions

### Chat Not Appearing
1. Verify backend is running on port 8000
2. Check browser console for JavaScript errors
3. Ensure Jarir.com is in the URL matches

### Styling Issues
1. Check Shadow DOM is properly created
2. Verify CSS injection in shadow root
3. Test in different browsers for compatibility

## 📦 Distribution

### Chrome Web Store
1. Build production bundle: `npm run build`
2. Create icons folder with required sizes (16x16, 48x48, 128x128)
3. Zip the extension folder
4. Upload to Chrome Developer Dashboard

### Firefox Add-ons
1. Ensure manifest.json is compatible with Firefox
2. Test with `web-ext run` for validation
3. Submit to Firefox Add-on store

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is part of the Jarir NLP suite. See the main repository for licensing information.

## 🆘 Support

For issues related to:
- **Extension UI/UX**: Create issue in this repository
- **AI Backend**: Check the main Jarir-NLP repository
- **Jarir.com Integration**: Verify website compatibility

---

Built with ❤️ for Jarir.com customers 