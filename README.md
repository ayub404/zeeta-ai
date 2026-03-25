Zeeta — AI Supply Chain Decision Engine



Zeeta is an experimental platform that helps turn real-time supply chain data into clear, actionable decisions.



Instead of just showing dashboards, Zeeta focuses on answering a simple question:



What should I do right now?



\---



&#x20;Overview



Supply chains break not because of missing data, but because decisions are slow and uncertain.



Zeeta brings together:

\- shipment data

\- external signals (weather, global events)

\- a lightweight decision layer



and turns them into:

\- risk signals

\- alerts

\- suggested actions



The goal is to reduce guesswork and help operators act faster.



\---



&#x20;Features



\- User authentication (JWT-based)

\- Shipment tracking

\- Risk detection using external data

\- Alerts system for disruptions

\- Decision suggestions (reroute, delay, adjust)

\- Web-based dashboard interface



\---



&#x20;Tech Stack



Backend:

\- FastAPI

\- PostgreSQL

\- Async SQLAlchemy

\- JWT authentication



Frontend:

\- HTML / CSS

\- Vanilla JavaScript



External data:

\- Open-Meteo (weather)

\- GDELT (global event data)



\---



&#x20;Project Structure





zeeta/

├── backend/

│   ├── main.py              ← entry point only

│   ├── database.py          ← DB connection + seeding

│   ├── models.py            ← SQLAlchemy tables

│   ├── schemas.py           ← Pydantic validation

│   ├── auth\_utils.py        ← JWT + password hashing

│   ├── routers/

│   │   ├── auth.py          ← /api/auth/\*

│   │   ├── shipments.py     ← /api/shipments/\*

│   │   ├── alerts.py        ← /api/alerts/\*

│   │   └── decisions.py     ← /api/decisions/\*

│   ├── services/

│   │   ├── weather.py       ← Open-Meteo integration

│   │   ├── live\_data.py     ← GDELT + weather alerts

│   │   └── stats.py         ← dashboard stats

│   ├── .env                 ← your DB credentials

│   └── requirements.txt

└── frontend/

&#x20;   ├── index.html           ← landing page

&#x20;   ├── signup.html          ← registration

&#x20;   ├── login.html           ← sign in

&#x20;   ├── dashboard.html       ← main app

&#x20;   ├── js/

&#x20;   │   ├── api.js           ← all API calls

&#x20;   │   ├── auth.js          ← session management

&#x20;   │   └── dashboard.js     ← rendering logic

&#x20;   └── css/

&#x20;       └── styles.css       ← all shared styles

