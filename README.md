<div>
  <img src="assets/kaust-academy-logo.png" alt="KAUST Academy Logo" height="80em" hspace='50'/> <img src="assets/jarir-logo.png" alt="Jarir Logo" height="50em" hspace='50'/> <img src="assets/kaust-logo.png" alt="KAUST Logo" height="80em"/>
</div>
<hr>

# **Jarir-NLP: Personalized AI Salesman**

## Overview
The Jarir NLP project is a unified data scraping and processing toolkit for extracting, cleaning, and analyzing product information from the Jarir Bookstore website. It supports multiple product categories including tablets, laptops, desktops, CPUs, and gaming PCs. The project is designed for research and educational purposes, with a focus on Natural Language Processing (NLP) and data science applications.

## Features
- **Unified Scraper:** Merges categories and extracts detailed product specifications.
- **Multi-threaded Scraping:** Fast and robust scraping using concurrent requests.
- **Data Cleaning:** Automated column mapping, normalization, and discount calculation.
- **CSV Export:** Cleaned data is saved in category-specific CSV files for further analysis.
- **Notebook Utilities:** Includes Jupyter notebooks for price normalization and exploratory data analysis.

## Project Structure

```
Jarir-NLP/
├── AIAgent/
│   ├── AIAgent.ipynb
│   ├── test.ipynb
│   ├── Tools.py
│   └── VaDGen.py
├── Jarir-scraper/
│   ├── final_scraper.py        # Main unified scraper
│   ├── main-scraper.py        # Legacy/alternative scraper
│   ├── *.csv                  # Output data files
│   └── unused_files/          # Old scripts and unused data
├── price.ipynb                # Price normalization notebook
├── renewed.py                 # Additional utilities
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
├── README.md                  # Project documentation
└── KAUST_AI_Poster.pptx       # Project poster
```

## Getting Started

### Prerequisites
- Python 3.8+
- Recommended: Create a virtual environment
- Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Scraper
Navigate to the `Jarir-scraper` directory and run:
```bash
python final_scraper.py
```
This will scrape all supported categories and output cleaned CSV files.

### Price Normalization
Open `price.ipynb` in Jupyter and run the notebook to add a normalized `price` column to each CSV file.

## Notebooks
- **AIAgent.ipynb:** AI agent utilities and experiments
- **price.ipynb:** Price column normalization and data cleaning
- **test.ipynb:** Testing and exploratory analysis

## Data Files
Output CSVs are generated for each product category:
- `jarir_tablets.csv`
- `jarir_laptops.csv`
- `jarir_2in1_laptops.csv`
- `jarir_desktops.csv`
- `jarir_cpu.csv`

- `jarir_gaming_pcs.csv`


## License
This project is for educational and research use only.

---
