
# Corteva Coding excercise

This project processes historical **weather and crop yield data**, computes **aggregated statistics**, and serves them via a **RESTful API** with **OpenAPI** documentation.

---

## Tech Stack

- **Python 3.10+**
- **Flask** + **Flask-Smorest** (for API & OpenAPI docs)
- **SQLAlchemy** (ORM)
- **PostgreSQL** (via Docker)
- **psycopg2** (for fast `COPY`-based ingestion)
- **Pytest** (for testing)
- **Docker** + **Docker Compose**

---

## 📁 Project Structure

```

corteva-challenge/
├── app/
│   ├── analysis.py            # Weather stats computation
│   ├── ingestion.py           # Bulk load (weather + yield)
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Marshmallow schemas
│   ├── yield_analysis.py      # Yield stats computation
│   └── routes/
│       ├── weather.py
│       ├── stats.py
│       ├── yield_records.py
│       └── yield_stats.py
├── tests/                     # Pytest unit tests
├── wx_data/                   # Weather input files (by station)
├── yld_data/                  # Yield input files (by station)
├── run.py                     # API entrypoint
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

````

---

## 🚀 Getting Started

#### 1. Clone the repo

```bash
git clone https://github.com/ChedvihasPunnam/corteva-challenge.git
cd corteva-challenge
````

#### 2. Ensure data files are present

If missing, pull them from the [Corteva template repo](https://github.com/corteva/code-challenge-template):

```bash
git clone https://github.com/corteva/code-challenge-template.git
cp -r code-challenge-template/wx_data code-challenge-template/yld_data ./
rm -rf code-challenge-template
```

#### 3. Start services

```bash
docker-compose up --build -d
```

#### 4. Ingest and process data

```bash
docker-compose exec web python -m app.ingestion
docker-compose exec web python -m app.analysis
docker-compose exec web python -m app.yield_analysis
```

#### 5. Access the API

* OpenAPI JSON: [http://localhost:5001/openapi.json](http://localhost:5001/openapi.json)

---

## 🔌 API Endpoints

All endpoints support pagination and filters like `station_id`, `year`, `date_from`, etc.

| Method | Endpoint              | Description              |
| ------ | --------------------- | ------------------------ |
| GET    | `/api/weather/`       | Raw weather data         |
| GET    | `/api/weather/stats/` | Aggregated weather stats |
| GET    | `/api/yield/`         | Raw yield data           |
| GET    | `/api/yield/stats/`   | Aggregated yield stats   |

### Example

```bash
curl "http://localhost:5001/api/weather/?station_id=USC00257715&date_from=1985-01-01" | jq
```

---

## ✅ Testing

Run unit tests with:

```bash
pytest -v
```

---

## 🌐 API Docs

* **OpenAPI Spec**: [http://localhost:5001/openapi.json](http://localhost:5001/openapi.json)
