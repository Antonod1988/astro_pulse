# ✨ AstroPulse — Personal Astrological Transit Forecast

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**AstroPulse** is a Streamlit-based web application that calculates and visualizes personal astrological transits. It uses the **Swiss Ephemeris** for precise planetary position calculations and provides interactive charts to help users understand upcoming astrological influences.

## 🌟 Features

- **Precise Transit Calculations** — powered by the Swiss Ephemeris (`pyswisseph`) for astronomical-grade accuracy
- **Interactive Energy Pulse Chart** — visualize the energetic intensity of transits over time with Plotly
- **Aspect Timeline** — Gantt-style chart showing when each transit aspect is active
- **House System Support** — calculates which astrological houses transiting planets affect
- **Auto-generated Interpretations** — each transit comes with a textual interpretation based on planet keywords, aspect type, and house placement
- **City Geocoding** — enter a city name and get coordinates automatically via OpenStreetMap Nominatim API
- **Bilingual UI** — full Russian and English interface support
- **Configurable Parameters** — customize orb size, minimum transit duration, planet selection, and aspect types
- **Deep Space Theme** — stunning dark cosmic UI with radial gradient background

## 📸 How It Works

1. Enter your **birth date, time, and timezone**
2. Specify your **location** (city search or manual coordinates)
3. Set the **forecast period** (default: 30 days)
4. Optionally adjust **advanced settings** (orb, aspects, planets)
5. Click **Calculate** — the app computes all active transits and displays:
   - 📊 **Energy Pulse** — a daily score chart (positive = harmonious, negative = tense)
   - 📅 **Aspect Timeline** — a visual timeline of all active transits
   - 🏠 **House Influences** — which life areas are affected
   - 📝 **Interpretations** — auto-generated descriptions for each transit

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Antonod1988/astro_pulse.git
cd astro_pulse

# Install dependencies
pip install -r requirements.txt
```

### Running

```bash
streamlit run main.py
```

Or on Windows, simply double-click `run_app.bat`.

The app will open in your browser at `http://localhost:8501`.

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web application framework |
| `pyswisseph` | Swiss Ephemeris bindings for planetary calculations |
| `pandas` | Data manipulation and transit table processing |
| `plotly` | Interactive charts (Energy Pulse, Aspect Timeline) |
| `pytz` | Timezone handling for birth time and transit conversion |

## 📁 Project Structure

```
astro_pulse/
├── main.py              # Main Streamlit app (UI + transit calculation logic)
├── interpretations.py   # Transit interpretation database & text generation
├── i18n.py              # Bilingual translations (RU/EN)
├── ephemeris/            # Swiss Ephemeris data files
├── requirements.txt     # Python dependencies
└── run_app.bat          # Windows launcher script
```

## 🔧 Configuration

All settings are available in the sidebar:

| Setting | Default | Description |
|---------|---------|-------------|
| Orb | 1° | Angular tolerance for aspect detection |
| Min Duration | 2 hours | Minimum transit duration to display |
| Planets | All | Which transiting planets to include |
| Aspects | Conjunction, Square, Trine, Opposition | Which aspect types to calculate |

## 🌐 Supported Aspects

| Aspect | Angle | Nature |
|--------|-------|--------|
| Conjunction | 0° | Neutral (depends on planets) |
| Sextile | 60° | Harmonious |
| Square | 90° | Tense |
| Trine | 120° | Harmonious |
| Opposition | 180° | Tense |

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Antonod1988** — [GitHub](https://github.com/Antonod1988)
