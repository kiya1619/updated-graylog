import requests
import pandas as pd
import io
from datetime import datetime







# Graylog Server Configuration
graylog_url = "http://10.10.101.116:9000/api/search/universal/relative"
username = "admin"  # Replace with your Graylog username
password = "admin@123"  # Replace with your Graylog password


params = {
    "query": "*", 
    "range": 100,  
    "limit": '100000',  
    "fields": "timestamp,source, message"  
}
response = requests.get(graylog_url, params=params, auth=(username, password))
csv_data = response.text
logs_df = pd.read_csv(io.StringIO(csv_data))
logs_df.to_csv("logs_come_after_every_5min.csv", index=False, quoting=1)
 
print('success')



