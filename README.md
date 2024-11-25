# Airflow and PostgreSQL Project: Sentiment Analysis of Reddit Comments

## Table of Contents
1. [Project Description](#project-description)
2. [Prerequisites](#prerequisites)
3. [Setup and Installation](#setup-and-installation)
4. [Usage](#usage)
5. [Troubleshooting](#troubleshooting)
6. [Stopping and Cleaning Up](#stopping-and-cleaning-up)

---

## Project Description
This project demonstrates the creation of an ETL pipeline to perform sentiment analysis on Reddit comments. The pipeline consists of the following steps:
- **Extract**: Gather comments from Reddit using the Reddit API.
- **Transform**: Process and clean the comments for analysis.
- **Load**: Store the results in a PostgreSQL database.
- - **Analyze**: Perform sentiment analysis using Hugging Face models.


The pipeline is managed and orchestrated using Apache Airflow, and the entire environment is containerized using Docker.

---

## Prerequisites
Before starting, ensure you have the following:
- Docker and Docker Compose installed.
- Python 3.8+ installed (if additional processing or virtual environment setup is required).

---

## Setup and Installation

### 1. Clone the Repository
Clone the project repository to your local machine:
```bash
git clone https://github.com/INWI_Sentiment_Analysis.git
cd your-repo-name

2. Initialize the Airflow Environment
Initialize the Airflow environment and create necessary database tables:

bash
Copy code
docker compose up airflow-init
3. Start the Services
Start the services in detached mode:

bash
Copy code
docker-compose up -d
This command starts the following services:

Airflow Webserver: Accessible at http://localhost:8080.
Airflow Scheduler: Orchestrates DAG tasks.
Airflow Worker: Executes tasks.
PostgreSQL Database: Stores the processed data.
Redis: Used for task queueing.
Note: If port 8080 is unavailable, modify the docker-compose.yaml file to change the port configuration.

Usage
1. Access the Airflow Web Interface
Access Airflow at http://localhost:8080.
Use the default credentials:

Username: airflow
Password: airflow
2. Activate the Sentiment Analysis Pipeline
Enable the DAG in the Airflow interface.
Trigger the DAG to:
Extract comments from Reddit using the API.
Clean and transform the comments.
Perform sentiment analysis using Hugging Face models.
Store the results in the PostgreSQL database.
3. Export Results
Export data from PostgreSQL to a CSV file:

bash
Copy code
docker exec -it <postgres_container_name> psql -U <POSTGRES_USER> -d <POSTGRES_DB> -c "COPY (SELECT * FROM sentiment_analysis_results) TO STDOUT WITH CSV HEADER" > results.csv
Troubleshooting
Port Conflict
If port 8080 is in use:

Identify the service using the port and stop it.
Update the docker-compose.yaml file to use another port.
Service Initialization Issues
If services fail to start:

bash
Copy code
docker-compose logs
This command provides detailed error messages.

Airflow Database Connection Errors
Ensure the sql_alchemy_conn parameter is correctly set in the airflow.cfg file.

Stopping and Cleaning Up
Stop and Remove Containers
bash
Copy code
docker-compose down
Stop Services Without Removing Them
bash
Copy code
docker-compose stop
License
This project is licensed under the MIT License.

Optional: Working in a Virtual Environment
If additional Python scripts are used for analysis or testing, activate the virtual environment:

On macOS/Linux:
bash
Copy code
source VirEnv/bin/activate
On Windows:
bash
Copy code
VirEnv\Scripts\activate

bash
Copy code
cd dags

bash
Copy code
py etl.py


