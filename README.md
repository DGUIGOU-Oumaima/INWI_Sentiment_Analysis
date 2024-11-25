Airflow and PostgreSQL Project
Table of Contents
Project Description
Prerequisites
Setup and Installation
Usage
Troubleshooting
Stopping and Cleaning Up
License
Project Description
This project demonstrates the creation of an ETL pipeline to extract data from Reddit, process it for sentiment analysis using Hugging Face models, and store the results in a PostgreSQL database. The pipeline is managed and orchestrated using Apache Airflow, with the environment containerized using Docker.

Prerequisites
Before starting, ensure the following:

Docker and Docker Compose are installed on your machine.
Python 3.8+ is installed (for additional processing or virtual environment setup).
Setup and Installation
1. Clone the Repository
Clone the project repository to your local machine:

bash
Copy code
git clone https://github.com/your-repo-name.git
cd your-repo-name
2. Download the Docker Compose File
Download the docker-compose.yaml file for Airflow using the following command:

bash
Copy code
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.3/docker-compose.yaml'
3. Configure Environment Variables
Set up the required environment variables:

For Linux:
bash
Copy code
echo -e "AIRFLOW_UID=$(id -u)" > .env
For Windows PowerShell:
powershell
Copy code
$env:USER_ID = (Get-Process -Id $pid).StartInfo.Environment["USERNAME"]
"AIRFLOW_UID=$env:USER_ID" | Out-File -FilePath .env -Encoding utf8
4. Initialize the Airflow Environment
Run the following command to initialize the Airflow environment and create the necessary database tables:

bash
Copy code
docker compose up airflow-init
5. Start the Services
To start the services in detached mode, run:

bash
Copy code
docker-compose up -d
This command will start the following services:

Airflow webserver (accessible at http://localhost:8080)
Airflow scheduler
Airflow worker
Airflow triggerer
PostgreSQL database
Redis
Note: If port 8080 is unavailable, modify the docker-compose.yaml file to change the port configuration.

Usage
Access the Airflow Web Interface
Once the services are running, access Airflow at http://localhost:8080. Use the default credentials to log in:

Username: airflow
Password: airflow
Activate the ETL Pipeline
Enable the DAG in the Airflow interface.
Trigger the DAG to:
Extract data from Reddit using the API.
Clean and transform the data.
Perform sentiment analysis with Hugging Face models.
Store the results in the PostgreSQL database.
Export Results
Export the data from PostgreSQL to a CSV file:

bash
Copy code
docker exec -it <postgres_container_name> psql -U <POSTGRES_USER> -d <POSTGRES_DB> -c "COPY (SELECT * FROM reddit_data) TO STDOUT WITH CSV HEADER" > output.csv
Troubleshooting
Port Conflict:
If port 8080 is in use, identify the service using the port and stop it or update the docker-compose.yaml file to use another port.

Service Initialization Issues:
If services fail to start, run docker-compose logs to check for detailed error messages.

Airflow Database Connection Errors:
Ensure the sql_alchemy_conn parameter is properly set in the airflow.cfg file.

Stopping and Cleaning Up
Stop and Remove Containers:
bash
Copy code
docker-compose down
Stop Services Without Removing Them:
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
source venv/bin/activate
On Windows:
bash
Copy code
venv\Scripts\activate