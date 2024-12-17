import os
import pandas as pd
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from django.http import HttpResponse
from django.core.mail import send_mail
import requests
from datetime import datetime
import re
import matplotlib.dates as mdates
from django.core.mail.backends.smtp import EmailBackend
matplotlib.use('Agg')
csv_path = os.path.join(settings.BASE_DIR, 'underlog/static/logs/logs_come_after_every_5min.csv')
#csv_path_met = os.path.join(settings.BASE_DIR, 'underlog/static/logs/correlated_data.xlsx')
logs_df = pd.read_csv(csv_path)
database_error = {
  "Access denied for user", "Access denied for user (using password: YES)", 
        "No database selected", "Unknown database", "Table already exists", 
        "Unknown table", "Unknown column", "Duplicate column name", "Duplicate key name", 
        "Duplicate entry for key", "You have an error in your SQL syntax", "Query was empty", 
        "Not unique table/alias", "Invalid default value", "Invalid default value for column", 
        "Too long column", "Too many columns", "Too many key parts", "Too many key parts specified", 
        "Too many key parts in a table", "Invalid table name", "Index length too long", 
        "Unknown character set", "Invalid time zone", "Invalid timezone conversion", 
        "Error in your SQL syntax", "Column count doesn't match value count", "Can't open file", 
        "Invalid SQLSTATE", "No data", "Unknown table type", "Access denied to database", 
        "Access denied to table", "Access denied to column", "Table doesn't exist", 
        "Can't create table", "Can't create database", "Invalid SQL statement", "Too many connections", 
        "Connection is not available", "Data too long for column", "Value out of range", 
        "Invalid group function", "Incorrect number of arguments", "Incorrect table definition", 
        "Index already exists", "Can't delete file", "Can't create index", "Invalid index", 
        "Duplicate column", "Invalid key", "Foreign key constraint failure", "Key length too long", 
        "Invalid key length", "Invalid foreign key constraint", "Duplicate foreign key", 
        "Can't create foreign key", "Incorrect foreign key", "Invalid data source", "Invalid handler", 
        "Incorrect syntax", "Invalid handle", "Access denied to stored procedure", 
        "Stored procedure not found", "Invalid stored procedure", "Can't update stored procedure", 
        "Permission denied for stored procedure", "Can't drop stored procedure", 
        "Can't create stored procedure", "Field not found", "Server shutdown", "Too many database connections", 
        "Incorrect data source", "Invalid SQL statement", "Invalid privilege", 
        "Cannot find row in given table", "Unknown column", "Unknown column in field list", "db"
    
}
network_error = {
    "Connection timeout", "Network unreachable", "Connection refused", "Connection reset", 
    "Host not found", "Connection aborted", "DNS lookup failure", "Connection lost", 
    "Network is down", "No route to host", "Port is closed", "Connection failed", 
    "Could not establish connection", "SSL handshake failure", "Timeout expired", 
    "Failed to connect to server", "Server not responding", "Connection closed by remote host", 
    "Network congestion", "Firewall blocking connection", "Connection throttling", 
    "IP address not allowed", "TCP connection reset", "Packet loss detected", 
    "Protocol error", "Out of memory", "Connection limit exceeded", "Connection pooling failed", 
    "Network protocol mismatch", "Transport error", "Socket error", "Unable to resolve host", 
    "TLS handshake error", "Connection timeout during handshake", "Unable to reach destination", 
    "Bad gateway", "Gateway timeout", "Network stack overflow", "Server timeout", 
    "Routing failure", "Failed to resolve domain", "Network authentication failed", 
    "Connection dropped", "Error establishing tunnel", "SSL certificate error", 
    "No network interface available", "Temporary network failure", "Bandwidth limit exceeded", 
    "Network interface error", "Network interface is down", "IP conflict detected", 
    "UDP connection error", "TCP timeout", "Failed to send data", "Failed to receive data", 
    "Ping request timed out", "Unreachable destination", "Server unreachable", "Route unavailable", 
    "Firewall block", "Unauthorized network access", "Too many open connections", 
    "Network error on transmission", "Failed to reconnect", "Data transfer error", 
    "Connection unstable", "Proxy server error", "Connection refused by proxy", 
    "Unable to reach DNS server", "Unexpected network disconnection"
    
    
}
authentication_error = {
    "Invalid credentials", "Authentication failed", "Login failed", "Incorrect username or password",
    "Account locked", "Account disabled", "Two-factor authentication failed", "Session expired",
    "Authentication timeout", "Invalid authentication token", "Token expired", 
    "Access denied", "Permission denied", "Authentication service unavailable", 
    "Invalid API key", "OAuth token error", "Login attempt exceeded", "Captcha validation failed",
    "User not found", "Invalid login attempt", "Authentication method not supported", 
    "Account not verified", "Account suspended", "Unrecognized device", "Password reset failed",
    "Invalid security answer", "Biometric authentication failed", "Security breach detected", 
    "Login attempts exceeded", "Invalid refresh token", "Failed to authenticate", "Login locked",
    "Authentication server error", "Authentication required", "Authorization failed", 
    "User authentication error", "SSL certificate error", "Unable to verify identity", 
    "Authentication expired", "Server refused connection", "Invalid session", "Access token revoked",
    "Missing credentials", "User not authorized", "User authentication required"
}
configuration_error = {
    "Invalid configuration", "Configuration file not found", "Missing configuration value",
    "Invalid configuration format", "Configuration error", "Failed to load configuration",
    "Incorrect settings", "Configuration mismatch", "Configuration not applied", 
    "Unsupported configuration option", "Syntax error in configuration file", 
    "Missing required parameter", "Configuration value out of range", "Invalid parameter value", 
    "Configuration conflict", "Failed to parse configuration", "Configuration update failed", 
    "Invalid default settings", "Permission denied to modify configuration", "Configuration file corrupted", 
    "Unable to read configuration", "Invalid config path", "Service misconfigured", 
    "Dependency missing in configuration", "Incorrect service configuration", 
    "Failed to apply changes to configuration", "Configuration timeout", "Default settings not found", 
    "Invalid environment configuration", "Network configuration error", "Configuration key missing",
    "Failed to save configuration", "Invalid input in configuration", "Configuration overwrite failed", 
    "Unresolved configuration variable", "Configuration not compatible with current version", 
    "Application misconfigured", "Configuration validation failed", "Failed to connect to config server",
    "System configuration error", "Service configuration conflict", "Configuration loading error",
    "Error reading config file", "Incompatible configuration settings", "Failed to initialize configuration", 
    "Configuration not found", "Configuration file read-only", "Database configuration error",
    "Application startup error due to configuration", "Resource allocation error in configuration"
}

logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)

def logs(request):

    logs_df = pd.read_csv(csv_path)
    logs_df['number'] = range(1, len(logs_df) + 1)
    logs_df['server_name'] = logs_df['source'].apply(lambda x: "Icinga Server" if "hq-osm-t03" in str(x)  
        else ("Windows Server" if "HQ-ISM-T01" in str(x)  
          else ("Graylog Server" if "hq-glg-t01" in str(x) 
                    else ("tsegaye" if "ITSMCC_PC08" in str(x)
                      else "") 
           )))

    
    search_source = request.GET.get('source', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
   
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)



    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    if search_source:
        # Filter the logs dataframe based on the selected source
        logs_df = logs_df[logs_df['source'].str.contains(search_source, case=False, na=False)]  


    if start_date:
        logs_df = logs_df[logs_df['timestamp'] >= start_date]
    if end_date:
        logs_df =  logs_df[logs_df['timestamp'] <= end_date]
    



    logs_list = logs_df.to_dict(orient="records")
    cnt = len(logs_list)
    paginator = Paginator(logs_list, 30)  
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'cnt':cnt,
        'search_source' :search_source,
        'start_date': start_date.strftime("%Y-%m-%d") if start_date else "",
        'end_date': end_date.strftime("%Y-%m-%d") if end_date else "",
        
    }
    return render(request, 'temp/logtable.html',  context)
    
def show(request):
    logs_df = pd.read_csv(csv_path) 


    
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')

    if logs_df['timestamp'].isnull().any():
        print("Invalid timestamps found. Dropping these rows.")
        logs_df = logs_df.dropna(subset=['timestamp'])
#############all sources that contibute log##########3
    #error_logs = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]
    top_sources = logs_df['source'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    top_sources.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Top 10 Sources Contributing to Logs', fontsize=16)
    plt.xlabel('Source', fontsize=14)
    plt.ylabel('Number of log', fontsize=14)
    plt.xticks(rotation=45, fontsize=12, ha='right')
    plt.tight_layout()

    # Save the chart as an image
    plot_image_path1 = os.path.join(settings.BASE_DIR, 'underlog/static/images/top10.png')
    plt.savefig(plot_image_path1)
    plt.close()

##################sources that have error log ##########################################
    error_logs = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]
    top_sources = error_logs['source'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    top_sources.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Top 10 Sources Contributing to Error Logs', fontsize=16)
    plt.xlabel('Source', fontsize=14)
    plt.ylabel('Number of Errors', fontsize=14)
    plt.xticks(rotation=45, fontsize=12, ha='right')
    plt.tight_layout()

    # Save the chart as an image
    plot_image_path1 = os.path.join(settings.BASE_DIR, 'underlog/static/images/toperror.png')
    plt.savefig(plot_image_path1)
    plt.close()




##############################################################################

    logs_df = logs_df.set_index('timestamp')
    error_logs = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]
    error_frequency = error_logs.resample('H').size()
    error_frequency_sorted = error_frequency.sort_values(ascending=False)


    def categorize_error(message):
        """Function to categorize error messages based on keywords."""
        if 'timeout' in message.lower() or 'connection' in message.lower():
            return 'NetworkError'
        elif 'auth' in message.lower() or 'Authentication failed' in message.lower():
            return 'AuthenticationError'
        elif 'database' in message.lower() or 'db' in message.lower():
            return 'DatabaseError'
        elif 'config' in message.lower() or 'missing' in message.lower() or 'invalid' in message.lower() or 'not found' in message.lower() or 'error loading config' in message.lower() or 'misconfigured' in message.lower():
            return 'ConfigurationError'
        '''elif '400 bad request' in message.lower():
            return 'ClientSideIssue'
        else:
            return 'GeneralError'''
        
    logs_df['error_category'] = logs_df['message'].apply(categorize_error)
    database_error_count = len(logs_df[logs_df['error_category'] == 'DatabaseError'])
    network_error_count = len(logs_df[logs_df['error_category'] == 'NetworkError'])
    Auth_count = len(logs_df[logs_df['error_category'] == 'AuthenticationError'])
    general_count = len(logs_df[logs_df['error_category'] == 'GeneralError'])
    config_count = len(logs_df[logs_df['error_category'] == 'ConfigurationError'])
    client_count = len(logs_df[logs_df['error_category'] == 'ClientSideIssue'])

    def categorize_errors(logs_df):
        """Apply the categorization function to each log entry."""
        # Filter out logs containing 'error' keyword
        error_logs = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]
        
        # Apply categorization to each error message
        error_logs['error_type'] = error_logs['message'].apply(categorize_error)
        
        # Count occurrences of each error type
        error_counts = error_logs['error_type'].value_counts()
        
        return error_counts, error_logs

    # Call the categorize function to get the error counts and categorized logs
    error_counts, error_logs = categorize_errors(logs_df)

    # Step 3: Plot the error types frequency
    plt.figure(figsize=(10, 6))
    sns.barplot(x=error_counts.index, y=error_counts.values, palette='viridis')
    plt.title("Error Types Frequency")
    plt.xlabel("Error Type")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot image to the static directory
    plot_image_path = os.path.join(settings.BASE_DIR, 'underlog/static/images/error_types_plot.png')
    plt.savefig(plot_image_path)
    #################################

    logs_df['error_type'] = logs_df['message'].apply(categorize_error)
    error_counts = logs_df['error_type'].value_counts()
    plt.figure(figsize=(12, 6))  # Set the figure size
    explode = [0.1 if count < 5 else 0 for count in error_counts]  # Adjust based on counts

    error_counts.plot(
        kind='pie',
        autopct=lambda p: f'{p:.1f}%\n({int(p * sum(error_counts) / 100)})',  # Percent + counts
        startangle=90,
        explode=explode,
        textprops={'fontsize': 12},  # Larger font for better readability
        wedgeprops={'edgecolor': 'black'}   # Apply a color scheme
    )
    plt.title("Distribution of Error Types")
    plt.ylabel("")  # Remove the y-label for a cleaner appearance
    plt.legend(title="Error Types", loc="upper right", bbox_to_anchor=(1.3, 0.9), fontsize=10, title_fontsize=12)
    plt.tight_layout()
    # Save the pie chart as an image
    error_types_plot_path = os.path.join(settings.BASE_DIR, 'underlog/static/images/error_types.png')
    plt.savefig(error_types_plot_path)
    plt.close()

    ###########timely error########################

    logs_df = pd.read_csv(csv_path)
    
    # Convert the 'timestamp' column to datetime
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')

    # Filter only logs containing the word 'error'
    error_logs_df = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]

    # Group by day and hour
    error_logs_df['day_hour'] = error_logs_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')

    # Count errors by day and hour
    error_trends_day_hourly = error_logs_df.groupby('day_hour').size()

    # Plot the error counts by day and hour
    plt.figure(figsize=(10, 6))
    error_trends_day_hourly.plot(kind='line', marker='o')
    plt.title("Error Trends by Day and Hour")
    plt.xlabel("Date and Hour")
    plt.ylabel("Error Count")
    plt.xticks(rotation=45)
    plt.grid(True)

    # Save the plot as an image file in the 'static/images' folder
    error_types_plot_path = os.path.join(settings.BASE_DIR, 'underlog/static/images/hourly_error.png')
    plt.savefig(error_types_plot_path)
    plt.close()
 
 
 
############################serverity level###################################################
    severity_keywords = {
    "Critical": ["critical", "fatal", "emergency"],
    "High": ["high", "severe", "major"],
    "Medium": ["medium", "moderate", "warning"],
    "Low": ["low", "minor", "info", "notice"]
    }
    logs_df["severity"] = "Unknown"
    for level, keywords in severity_keywords.items():
        logs_df.loc[logs_df['message'].str.contains('|'.join(keywords), case=False, na=False), 'severity'] = level
    severity_counts = logs_df['severity'].value_counts()
    plt.figure(figsize=(8, 6))
    severity_counts.plot(kind='bar', color=['red', 'orange', 'yellow', 'green', 'gray'], edgecolor='black')
    plt.title('Log Distribution by Severity Level', fontsize=16)
    plt.xlabel('Severity Level', fontsize=14)
    plt.ylabel('Number of Logs', fontsize=14)
    plt.xticks(rotation=45, fontsize=12, ha='center')
    plt.tight_layout()

    # Save the chart as an image
    severity_plot_path = os.path.join(settings.BASE_DIR, 'underlog/static/images/severity.png')
    plt.savefig(severity_plot_path)
    plt.close()
    









###############################################################################


    context = {
        'error_counts': error_counts,  # Error type frequency counts
        'plot_image': 'images/error_types_plot.png',
        'error_types_plot': 'images/error_types.png',  # Path to the saved plot
        'error_logs': error_logs,  # Logs with categorized error types
        'database_error_count': database_error_count,
        'network_error_count' : network_error_count,
        'Auth_count' : Auth_count,
        'general_count' :general_count,
        'config_count' :config_count,
        'client_count': client_count,
        'ip_error_plot' : 'images/ip_error_plot.png',
#moved from trend

        'top_sources_plot': 'images/top10.png',
        'top_error_sources': 'images/toperror.png',
        'severity': 'images/severity.png',
        'error_frequency_plot': 'images/error_frequency.png',
        'severity_image': 'images/severity_distribution.png',
        'source_image': 'images/error_sources.png',
        'error_frequency': error_frequency_sorted,
        'hourly_errorr':'images/hourly_error.png',
        'serverity_plot':'images/severity_chart.png',
       
    }
    
    return render(request, 'temp/show.html', context)

def errorcategory(request):

    logs_df = pd.read_csv(csv_path)
    
    

    # Step 2: Categorize errors
    def categorize_error(message):
        
        message_lower = message.lower()
        """Function to categorize error messages based on keywords."""
        if any(db_error.lower() in message_lower for db_error in configuration_error):
            return 'ConfigurationError'
        elif any(db_error.lower() in message_lower for db_error in authentication_error):
            return 'AuthenticationError'
        elif any(db_error.lower() in message_lower for db_error in database_error):
            return 'DatabaseError'
        elif any(db_error.lower() in message_lower for db_error in network_error):
            return 'NetworkError'
        
        
      
        else:
            return 'GeneralError'''

    
        
    logs_df['error_category'] = logs_df['message'].apply(categorize_error)


    database_error_count = len(logs_df[logs_df['error_category'] == 'DatabaseError'])
    network_error_count = len(logs_df[logs_df['error_category'] == 'NetworkError'])
    Auth_count = len(logs_df[logs_df['error_category'] == 'AuthenticationError'])
    general_count = len(logs_df[logs_df['error_category'] == 'GeneralError'])
    config_count = len(logs_df[logs_df['error_category'] == 'ConfigurationError'])
    client_count = len(logs_df[logs_df['error_category'] == '404badrequest'])

    total = database_error_count + network_error_count + Auth_count + general_count + config_count + client_count

    mylog = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]
    top_error_messagess = mylog['message'].value_counts().head(10)
    top_error_messages_dict = top_error_messagess.to_dict()

    def categorize_errors(logs_df):
        """Apply the categorization function to each log entry."""
        # Filter out logs containing 'error' keyword
        error_logs = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]
        
        # Apply categorization to each error message
        error_logs['error_type'] = error_logs['message'].apply(categorize_error)
        
        # Count occurrences of each error type
        error_counts = error_logs['error_type'].value_counts()
        
        
        return error_counts, error_logs

    # Call the categorize function to get the error counts and categorized logs
    error_counts, error_logs = categorize_errors(logs_df)

    logs_df['error_type'] = logs_df['message'].apply(categorize_error)
    error_counts = logs_df['error_type'].value_counts()
    plt.figure(figsize=(6, 6))  # Set the figure size
    explode = [0.1 if count < 5 else 0 for count in error_counts]  # Adjust based on counts


    top_error_messages = logs_df['message'].value_counts().head(10)

    
    context = {
        'error_counts': error_counts,      
        'database_error_count': database_error_count,
        'network_error_count' : network_error_count,
        'Auth_count' : Auth_count,
        'general_count' :general_count,
        'config_count' :config_count,
        'top_error_messages': top_error_messages,
        'client_count': client_count,
        'top_error_messagess':top_error_messages_dict,
        
 
        'total': total
 
    }
    

    # Return the response with data to the template
    return render(request, 'temp/errorcategory.html', context)

def network(request):

    logs_df = pd.read_csv(csv_path)
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
    
    if logs_df['timestamp'].isnull().any():
       
        logs_df = logs_df.dropna(subset=['timestamp'])



    def categorize_error(message):
        message_lower = str(message).lower()  # Ensure the message is a string and convert it to lowercase
        if any(db_error.lower() in message_lower for db_error in network_error):
            return 'NetworkError'
        else:
            return 'OtherError'
 
    logs_df['error_type'] = logs_df['message'].apply(categorize_error)
    network_error_logs = logs_df[logs_df['error_type'] == 'NetworkError']
    cnt = len(network_error_logs)
    #regex_pattern = '|'.join(map(re.escape, network_error))
    

    #network_error_logs = logs_df[logs_df['message'].str.contains(regex_pattern, case=False, na=False)]
    #cnt = len(network_error_logs)
    context = {
        'network_error_logs': network_error_logs,
        'cnt' : cnt
    }

    
    return render(request, 'temp/network.html', context)

def database(request):
    logs_df = pd.read_csv(csv_path)
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
    if logs_df['timestamp'].isnull().any():
        print("Invalid timestamps found. Dropping these rows.")
        logs_df = logs_df.dropna(subset=['timestamp'])

   

    # Create a regular expression pattern that matches any of the database error messages
    regex_pattern = '|'.join(map(re.escape, database_error))

    # Filter the logs where the 'message' column contains any of the database errors
    database_error_logs = logs_df[logs_df['message'].str.contains(regex_pattern, case=False, na=False)]

    # Count the number of database error logs
    cnt = len(database_error_logs)

    # Apply the categorize_database_error function to each message in the 'message' column
 

    # Prepare the context for rendering
    context = {
        'database_error_logs': database_error_logs,
        'cnt': cnt
    }

    return render(request, 'temp/database.html', context)

def general(request):
    logs_df = pd.read_csv(csv_path)
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)
    def categorize_error(message):
        message_lower = message.lower()
        """Function to categorize error messages based on keywords."""
        if any(db_error.lower() in message_lower for db_error in network_error):
            return 'NetworkError'
        elif any(db_error.lower() in message_lower for db_error in authentication_error):
            return 'AuthenticationError'
        elif any(db_error.lower() in message_lower for db_error in database_error):
            return 'DatabaseError'
        elif any(db_error.lower() in message_lower for db_error in configuration_error):
            return 'ConfigurationError'
        else:
            return 'GeneralError'''
       
    

    # Filter general errors (errors that are not network, authentication, or database-related)
    general_error_logs = logs_df[logs_df['message'].apply(lambda msg: categorize_error(msg) == 'GeneralError')]
    general_error_logs['formatted_timestamp'] = general_error_logs['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    
    cnt = len(general_error_logs)

    context = {'general_error_logs': general_error_logs,
               'cnt' : cnt
               
               
               }
    return render(request, 'temp/general.html', context)

def auth(request):

    logs_df = pd.read_csv(csv_path)
    
    # Ensure timestamp is properly formatted
    
    if logs_df['timestamp'].isnull().any():
        print("Invalid timestamps found. Dropping these rows.")
        logs_df = logs_df.dropna(subset=['timestamp'])

    regex_pattern = '|'.join(map(re.escape, authentication_error))

    # Filter the logs where the 'message' column contains any of the database errors
    auth_error_logs = logs_df[logs_df['message'].str.contains(regex_pattern, case=False, na=False)]
    cnt = len(auth_error_logs)    

    # Render database error template
    context = {'auth_error_logs': auth_error_logs,
               'cnt':cnt,
       
               
               }
    return render(request, 'temp/auth.html', context)

def configuration(request):



    logs_df = pd.read_csv(csv_path)
    
    # Ensure timestamp is properly formatted
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
    if logs_df['timestamp'].isnull().any():
        print("Invalid timestamps found. Dropping these rows.")
        logs_df = logs_df.dropna(subset=['timestamp'])

    regex_pattern = '|'.join(map(re.escape, configuration_error))

    # Filter the logs where the 'message' column contains any of the database errors
    conf_error_logs = logs_df[logs_df['message'].str.contains(regex_pattern, case=False, na=False)]    
    cnt = len(conf_error_logs)

    #rare error logs
   

    # Render database error template
    context = {'conf_error_logs': conf_error_logs,
               'cnt':cnt,
       
               
               }
    return render(request, 'temp/configuration.html', context)
    
def badrequest(request):
    logs_df = pd.read_csv(csv_path)
    
    # Ensure timestamp is properly formatted
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
    if logs_df['timestamp'].isnull().any():
        logs_df = logs_df.dropna(subset=['timestamp'])

    badrequest = logs_df[logs_df['message'].str.contains('400 bad request', case=False, na=False)]
    cnt = len(badrequest)
    errortype = '400 bad request'

    #rare error logs
   
    

    # Render database error template
    context = {'badrequest': badrequest,
               'cnt':cnt,
               'errortype':errortype
       
               
               }
    return render(request, 'temp/badrequest.html', context)

def send_telegram_message(bot_token, chat_id, message):

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=params)
    return response.json()

def send_email_view(request):
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')

    error_logs_df = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]

# Group by day and hour (now only with error logs)
    error_logs_df['day_hour'] = error_logs_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')

    # Count errors by day and hour
    error_trends_day_hourly = error_logs_df.groupby('day_hour').size()

    # Plot the error counts by day and hour
    error_trends_day_hourly.plot(kind='line', marker='o')
    plt.title("Error Trends by Day and Hour")
    plt.xlabel("Date and Hour")
    plt.ylabel("Error Count")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()
        
    

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        recipient = request.POST.get('recipient')
        recipient_list = [recipient] if recipient else []

        if recipient_list:
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                return HttpResponse("Email sent to " + recipient)
            except Exception as e:
                return HttpResponse(f"Error sending email: {e}")
        else:
            return HttpResponse("No recipient provided.")


    return render(request, 'temp/email.html', )


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
     
       
        if username == 'admin' and password == 'admin':
            return redirect('logs')
        else:
            return redirect('login')
    return render(request, 'temp/login.html')


def source_cat(request):
    logs_df = pd.read_csv(csv_path)

    source_counts = logs_df['source'].value_counts()
    top_sources = source_counts.head(10)

    context = {

        'top_sources': top_sources
    }

    return render(request, 'temp/source_cat.html', context)

def test(request):
    return render(request, 'temp/test.html')

def is_critical(message):
    # List of critical keywords
    critical_keywords = {'critical', 'fatal', 'emergency'}
    
    
    # Convert message to lowercase for case-insensitive matching
    message = message.lower()
    
    # Check if any word in the critical set exists in the message
    return any(word in message for word in critical_keywords)
def criticall(request):
    logs_df['severity'] = logs_df['message'].apply(lambda x: 'Critical' if is_critical(x) else 'Not Critical')
    critical_messages = logs_df[logs_df['severity'] == 'Critical']
    critical_messages_list = critical_messages[['timestamp', 'source', 'message']].to_dict('records')
    cnt = len(critical_messages_list)
    context = {
        'critical_messages': critical_messages_list,
        'cnt':cnt
        
    }
    
   

    
    
    return render(request, 'temp/criticall.html', context)