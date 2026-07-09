# Health Data Dashboard

Live Demo: https://neelam-xqf9.onrender.com

A small Flask app for exploring `health_data.csv` (1,200 patient health records).

## Setup

```bash
pip install flask --break-system-packages
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Structure

- `app.py` — Flask backend, loads the CSV into memory and exposes JSON APIs
- `templates/index.html` — dashboard UI (filters, stat cards, charts, paginated table)
- `data/health_data.csv` — the dataset

## Features

- Filter all views by Gender and Risk Level
- Summary stat cards (avg/min/max) for key metrics
- Risk level breakdown donut chart
- Configurable scatter plot (pick any two numeric fields)
- Paginated, sortable-by-column-order records table

## API endpoints

- `GET /api/summary?gender=&risk=` — aggregate stats
- `GET /api/records?gender=&risk=&page=&per_page=` — paginated raw rows
- `GET /api/scatter?gender=&risk=&x=&y=` — x/y points for the scatter chart
