# 🍔 Big Mac Index Dashboard

An editorial-style Streamlit dashboard visualising **The Economist's Big Mac Index** — purchasing power parity through the world's most iconic fast-food item.

---

## Folder Structure

```
bigmac_dashboard/
├── data/
│   └── big-mac.csv          ← Place the dataset here
├── .streamlit/
│   └── config.toml
├── app.py
├── charts.py
├── filters.py
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get the Dataset
Download `big-mac.csv` from TidyTuesday 2020:
```
https://github.com/rfordatascience/tidytuesday/blob/main/data/2020/2020-12-22/big-mac.csv
```
Place it inside the `data/` folder.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```

Your browser will open at `http://localhost:8501`.

---

## Features

| Section | Charts |
|---------|--------|
| **Price Landscape** | Bar ranking · Lollipop over/under-valuation |
| **Time Evolution** | Global avg trend · Ridgeline distributions · Heatmap |
| **Valuation Analysis** | Raw vs Adj scatter · Area trajectories · Violin · Biggest movers |
| **Statistical Deep Dive** | Histogram · Box-per-year · Country bubble chart |
| **Data Explorer** | Country summary table · Raw data table · CSV exports |

### Sidebar Controls
- **Year Range** — Filter by any period in the dataset
- **Countries** — Multi-select specific countries (blank = all)
- **Price Metric** — Toggle between Raw and GDP-Adjusted index
- **Top N** — Control how many countries appear in ranked charts

---

## Design Notes

The dashboard uses an **editorial / luxury print** aesthetic:
- **Typography**: Playfair Display (serif headers) + DM Mono (labels/data) + DM Sans (body)
- **Color palette**: Deep black (#0a0a0a) with warm gold (#c8a96e) accents
- **Completely different** from the original amber/navy Pell Grant dashboard
- Every chart is export-able as PNG via the ↓ Export button

---

*Data source: The Economist · TidyTuesday 2020*
