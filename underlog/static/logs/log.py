import requests
import pandas as pd
import io
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine

from urllib.parse import quote





import requests
import pandas as pd
import io
from sqlalchemy import create_engine

# Graylog Server Configuration
graylog_url = "http://10.10.101.116:9000/api/search/universal/relative"
username = "admin"  # Replace with your Graylog username
password = "admin@123"  # Replace with your Graylog password

# PostgreSQL Configuration
db_host = "localhost"
db_name = "graylog"
db_user = "postgres"
db_password = quote("admin@123")

# Fetch logs from Graylog
params = {
    "query": "*", 
    "range": 100,  # Logs from the last hour
    "limit": 100000,  
    "fields": "timestamp,source,message"  # Relevant fields
}

response = requests.get(graylog_url, params=params, auth=(username, password))

# Check if the request was successful
if response.status_code != 200:
    raise Exception(f"Error fetching logs: {response.status_code}, {response.text}")

# Convert logs to pandas DataFrame
csv_data = response.text

try:
    logs_df = pd.read_csv(io.StringIO(csv_data))
except Exception as e:
    print(f"Error parsing CSV data: {e}")
    raise

# Convert timestamp column to datetime
logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')

# Ensure valid database connection string
engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}")

# Insert logs into PostgreSQL
try:
    logs_df.to_sql('logs', engine, if_exists='replace', index=False)
    print("Logs successfully inserted into the database.")
except Exception as e:
    print(f"Error inserting logs into the database: {e}")
