# 📈 AutoPrice Monitor

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**AutoPrice Monitor** is a modern, full-stack e-commerce price tracking and analytics platform. It enables users to automatically track product prices across major e-commerce stores (Amazon, Noon, Jumia, etc.), log historical price variations, and visualize price fluctuations through interactive charts and real-time metrics.

---

## ✨ Key Features

- **🔐 Animated Multi-User Authentication**:
  - Secure login and registration system with SHA-256 password hashing.
  - Custom UI/UX featuring CSS animations, smooth transitions, and responsive dark-mode containers.

- **🛒 Smart Web Scraping Engine**:
  - Automated web scraping logic to extract real-time product prices from major e-commerce platforms.
  - Store identification badges (Amazon, Noon, Jumia).

- **📊 Price Analytics & Historical Tracking**:
  - Interactive line charts tracking historical price trends over time.
  - Key performance metrics: Current Price, Lowest Recorded Price, Highest Recorded Price, and Total Fluctuation.

- **🔄 One-Click Price Sync**:
  - Batch price update functionality to refresh all tracked products with a single click.

- **🎨 Modern Aesthetic & Micro-Interactions**:
  - Custom Emerald Green / Light Mint theme.
  - Continuous animated SVG cart icons and glowing gradient section borders for an enhanced UX.

---

## 🛠️ Tech Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **Backend & Logic**: Python 3.10+
- **Data Scraping**: `BeautifulSoup4`, `requests`
- **Data Manipulation & Storage**: `pandas`, CSV storage
- **Security & Config**: `hashlib` (SHA-256), `python-dotenv`

---

## 📁 Project Structure

```text
AutoPrice-Monitor/
├── app.py              # Main application entrypoint (Dashboard & Animated Login UI)
├── scraper.py          # Web scraping logic for e-commerce platforms
├── run_app.py          # Automated launcher script
├── requirements.txt    # Python package dependencies
├── .env.example        # Environment variables configuration template
├── users.csv           # User accounts repository
├── products.csv        # Tracked products dataset
└── price_history.csv   # Historical price analytics log