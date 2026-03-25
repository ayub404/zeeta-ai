# Zeeta MVP — Setup Guide

## Project Structure
```
zeeta/
├── frontend/
│   └── index.html        # Dashboard UI (open directly in browser)
├── backend/
│   └── main.py           # FastAPI backend
└── README.md
```

## Backend Setup

```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Run the API server
cd backend
uvicorn main:app --reload --port 8000

# API docs available at:
# http://localhost:8000/docs
```

## Frontend Setup
Just open `frontend/index.html` in your browser.
To connect to the live backend, update the fetch URLs in index.html to point to `http://localhost:8000`.

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/stats | Dashboard summary stats |
| GET | /api/shipments | List all shipments |
| GET | /api/shipments/{id} | Single shipment detail |
| GET | /api/alerts | Active risk alerts |
| POST | /api/decisions/{id} | Get AI decision for shipment |

## Next Steps
1. Connect real data sources (MarineTraffic, weather APIs)
2. Add user authentication
3. Build the AI decision engine with real ML model
4. Add a database (PostgreSQL recommended)
5. Deploy backend to Railway or Render (free tier)
