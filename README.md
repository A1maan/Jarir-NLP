<div style="display: flex; justify-content: flex-start; align-items: center; gap: 3em;">
  <img src="assets/kaust-academy-logo.png" alt="KAUST Academy Logo" height="100em" hspace='50'/> <img src="assets/jarir-logo.png" alt="Jarir Logo" height="55em" hspace='50'/> <img src="assets/kaust-logo.png" alt="KAUST Logo" height="100em"/>
</div>
<hr>

# **Jarir-NLP: Personalized AI Salesman**

## Overview
The Jarir-NLP project is an AI-powered natural language processing system that combines web scraping, intelligent product search, and conversational AI to create a personalized shopping assistant for Jarir Bookstore. The system features a browser extension that provides real-time product recommendations and comparisons directly on the Jarir website, powered by a FastAPI backend and advanced NLP capabilities.

## Features
- **AI-Powered Chat Interface:** Interactive browser extension with conversational product search
- **Intelligent Product Matching:** Advanced search and recommendation algorithms
- **Multi-threaded Web Scraping:** Fast and robust data extraction with image handling
- **Real-time Backend API:** FastAPI server with auto-reload for development
- **Data Processing Pipeline:** Automated cleaning, normalization, and CSV export
- **Multi-category Support:** Handles laptops, tablets, gaming PCs, desktops, and more
- **Browser Integration:** Seamless integration with Jarir's website via content scripts
- **Responsive UI Components:** Modern React-based chat interface with TypeWriter effects

## Project Structure

```
Jarir-NLP/
├── AIAgent/
│   ├── AIAgent.ipynb          # Main AI agent development notebook
│   ├── dbSearch.ipynb         # Database search experiments
│   ├── dbSearch.py           # Database search implementation
│   ├── ST.py                 # Streamlit interface components
│   ├── test.ipynb            # Testing and experimentation
│   └── Tools.py              # AI agent tools and utilities
├── backend/
│   ├── agent_core.py         # Core AI agent logic
│   ├── app.py               # FastAPI backend application
│   ├── dbSearch.py          # Backend database search functionality
│   └── Tools.py             # Backend utility tools
├── Jarir-scraper/
│   ├── initial_scraper.py    # Initial web scraping implementation
│   ├── scraper_with_img.py   # Enhanced scraper with image handling
│   ├── *.csv                # Scraped product data files
│   │   ├── jarir_AIO.csv     # All-in-one computers
│   │   ├── jarir_gaming_pcs.csv # Gaming PCs
│   │   ├── jarir_laptops.csv # Laptops
│   │   ├── jarir_tablets.csv # Tablets
│   │   └── jarir_twoin1_laptops.csv # 2-in-1 laptops
│   ├── csv_cleanup/         # Data cleaning utilities
│   └── unused_files/        # Legacy scrapers and unused data
├── web_extension/
│   ├── manifest.json        # Browser extension manifest (Manifest V3)
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── ChatBubble.jsx    # Individual chat messages
│   │   │   ├── ChatWidget.jsx    # Main chat interface
│   │   │   ├── MessageInput.jsx  # User input component
│   │   │   ├── MessageList.jsx   # Message container
│   │   │   ├── ProductCard.jsx   # Product display cards
│   │   │   ├── ProductStrip.jsx  # Product carousel
│   │   │   └── TypewriterText.jsx # Animated text effects
│   │   ├── content.js       # Content script injection
│   │   ├── hooks/          # Custom React hooks
│   │   │   ├── useChat.js       # Chat state management
│   │   │   └── useDraggable.js  # Drag functionality
│   │   ├── styles/         # CSS styling
│   │   └── utils/          # Utility functions
│   │       ├── markdownParser.jsx # Markdown rendering
│   │       ├── productUtils.js   # Product data helpers
│   │       └── shadowDom.js      # Shadow DOM utilities
│   ├── build.js            # Build configuration
│   ├── package.json        # Node.js dependencies
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   └── vite.config.js      # Vite build configuration
├── notes/                   # Development notes and documentation
├── requirements.txt         # Python dependencies
├── setup.sh                # Environment setup script
└── README.md               # This documentation
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- Modern web browser (Chrome/Edge recommended)
- Recommended: Create a virtual environment

### Installation
1. **Clone and setup the environment:**
   ```bash
   git clone <repository-url>
   cd Jarir-NLP
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies and build the extension:**
   ```bash
   cd web_extension
   npm install
   npm run build
   ```

### Running the System

#### 1. Start the Backend Server
```bash
cd backend
uvicorn app:app --reload
```
The FastAPI server will start on `http://localhost:8000` with auto-reload enabled.

#### 2. Load the Browser Extension
1. Open your browser and go to `chrome://extensions/` (or `edge://extensions/`)
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `web_extension/dist` folder
5. The extension should now be loaded and active

#### 3. Use the AI Salesman
1. Navigate to [jarir.com](https://jarir.com)
2. The chat widget will appear on the page
3. Start conversing with the AI:
   - "Show me gaming laptops under 5000 SAR"
   - "I need a tablet for digital art"
   - "Compare these laptops for performance"
   - "What's the best value gaming PC?"

### Data Collection
Run the web scraper to update product data:
```bash
cd Jarir-scraper
python scraper_with_img.py
```

## Development

### Backend Development
```bash
cd backend
uvicorn app:app --reload  # Auto-reloads on file changes
```

### Extension Development
```bash
cd web_extension
npm run dev  # Development mode with hot reload
```

### Technology Stack
- **Backend:** FastAPI, Python, Pandas, NLP libraries
- **Frontend:** React, Tailwind CSS, Vite
- **Extension:** Manifest V3, Content Scripts, Shadow DOM
- **Data Processing:** Multi-threaded scraping, CSV handling
- **AI/ML:** Language model integration for conversational AI

## Notebooks
- **AIAgent.ipynb:** AI agent development and experimentation
- **dbSearch.ipynb:** Database search algorithm testing
- **test.ipynb:** General testing and exploratory analysis

## Data Files
The system generates and uses CSV files for each product category:
- `jarir_tablets.csv` - Tablet specifications and pricing
- `jarir_laptops.csv` - Laptop data with detailed specs
- `jarir_twoin1_laptops.csv` - 2-in-1 convertible laptops
- `jarir_gaming_pcs.csv` - Gaming desktop computers
- `jarir_AIO.csv` - All-in-one computer systems

## API Documentation
Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## Troubleshooting

### Common Issues
- **Backend not starting:** Ensure you're in the `backend/` directory and all dependencies are installed
- **Extension not loading:** Verify the build completed successfully and you're loading the correct `dist` folder
- **Chat widget not appearing:** Check that the backend is running and browser console for any errors
- **CORS errors:** The backend is configured for development; check CORS settings if deploying

### Development Tips
- Use browser DevTools to inspect the extension's content script
- Check the FastAPI logs for backend debugging
- The chat widget uses Shadow DOM for style isolation

## Contributing
This project is developed for educational and research purposes. When contributing:
1. Follow the existing code structure
2. Test both backend API and extension functionality
3. Update documentation for any new features
4. Ensure cross-browser compatibility for the extension

## License
This project is for educational and research use only. Developed as part of KAUST Academy research initiatives.

---

**Developed by KAUST Academy in collaboration with Jarir Bookstore for NLP and AI research purposes.**