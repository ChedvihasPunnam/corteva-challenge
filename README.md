
# Corteva Coding excercise

This project processes historical **weather data**, computes **aggregated statistics**, and serves them via a **RESTful API** with **OpenAPI** documentation.

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

## Project Structure

```

corteva-challenge/
├── app/
│   ├── analysis.py            # Weather stats computation
│   ├── ingestion.py           # Bulk load
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Marshmallow schemas
│   └── routes/
│       ├── weather.py
│       ├── stats.py
├── tests/                     # Pytest unit tests
├── wx_data/                   # Weather input files (by station)
├── run.py                     # API entrypoint
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

````

---

## Getting Started

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
docker compose up --build -d 
```

#### 4. Ingest and process data

```bash
docker compose exec web python -m app.ingestion
docker compose exec web python -m app.analysis
```

#### 5. Access the API

* OpenAPI JSON: [http://localhost:5001/openapi.json](http://localhost:5001/openapi.json)

---

## API Endpoints

All endpoints support pagination and filters like `station_id`, `year`, `date_from`, etc.

| Method | Endpoint              | Description              |
| ------ | --------------------- | ------------------------ |
| GET    | `/api/weather/`       | Raw weather data         |
| GET    | `/api/weather/stats/` | Aggregated weather stats |

### Example

```bash
curl "http://localhost:5001/api/weather/?station_id=USC00257715&date_from=1985-01-01" | jq
```

---

## Testing

Run unit tests with:

```bash
pytest -v
```

---

## API Docs

* **OpenAPI Spec**: [http://localhost:5001/openapi.json](http://localhost:5001/openapi.json)

## Cloud Deployment Strategy

### Current Setup (Manual Deployment on AWS EC2)

* An **EC2 instance** was provisioned on AWS (Amazon Linux 2).
* On the EC2 machine:

  * Docker and Docker Compose were installed.
  * This repository was cloned.
  * The application was built and started using `docker-compose up -d`.
* The app includes:

  * A **Flask API server** container running on port `5001`.
  * A **PostgreSQL database** container.
* Security Group settings were updated to open port **5001** to the public.
* Data ingestion and analysis scripts were run manually using:

  ```bash
  docker-compose exec web python -m app.ingestion
  docker-compose exec web python -m app.analysis
  ```
* The API is accessible at:

  ```
  http://3.85.22.222:5001/api/weather/
  ```

---

### CI/CD Automation Plan (To Be Implemented)

To automate the deployment process, GitHub Actions can be used to build and deploy updates automatically to the EC2 instance.

#### Tools:

* **GitHub Actions** – to automate deployment steps
* **AWS EC2** – hosting the app
* **SSH keys** – to securely connect from GitHub to EC2

#### Workflow Overview:

1. **Trigger:**

   * Any code `push` to the `master` branch triggers the workflow.

2. **GitHub Action Steps:**

   * Connect to the EC2 instance via SSH.
   * Pull the latest changes from GitHub.
   * Rebuild and restart Docker containers:

     ```bash
     docker-compose down
     docker-compose up -d --build
     ```
   * Optionally re-run ingestion/analysis:

     ```bash
     docker-compose exec web python -m app.ingestion
     docker-compose exec web python -m app.analysis
     ```


## Cloud Deployment and Automation Strategy

This project has been deployed on an **Amazon EC2 instance** using Docker and Docker Compose. The web API and PostgreSQL database are containerized and run together in a local Docker network.

### Current EC2-Based Deployment Approach

- The app is deployed on an AWS EC2 instance running Amazon Linux.
- We use `docker-compose up -d` to run the FastAPI service and PostgreSQL database.
- The ingestion logic can be triggered manually by running:
  
  ```bash
  docker-compose exec web python -m app.ingestion
  ```

* The API becomes publicly accessible via `http://3.85.22.222:5001/api/weather/` once security group ports are opened (port 5001).


## Future Automation Strategy

To make the ingestion process scalable and fully automated, we can enhance the architecture using AWS services:

### Option 1: File-Triggered Ingestion via S3 + Lambda/ECS

* Upload new data files into an S3 bucket.
* Configure **S3 Event Notifications** to trigger:

  * An **AWS Lambda function**, or
  * An **ECS Fargate task**
* This function/task runs the ingestion logic (`app.ingestion`) and loads data into a hosted PostgreSQL database (e.g., Amazon RDS).

### Option 2: Scheduled Ingestion via Cron

* Use **Amazon EventBridge (CloudWatch Events)** to trigger a Lambda or ECS task on a fixed schedule (e.g., daily at midnight).
* The job pulls files from a source (e.g., S3 or FTP), ingests the data, and runs analysis.

---
