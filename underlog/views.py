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
import csv
import plotly.express as px
from django.core.mail.backends.smtp import EmailBackend
import kaleido
import plotly.io as pio
import plotly.graph_objects as go
from sqlalchemy import create_engine
from urllib.parse import quote

# PostgreSQL Configuration
db_host = "localhost"
db_name = "graylog"
db_user = "postgres"
db_password = quote("admin@123")
engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}")


matplotlib.use('Agg')


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
        "Cannot find row in given table", "Unknown column", "Unknown column in field list","Lock wait timeout exceeded",
        "Deadlock found when trying to get lock", "Server gone away", "Too many open files", "Can't open table", 
    "Cannot connect to MySQL server", "Table is read only", "Table is full",     "Host is blocked", "Can't allocate memory", "Access denied for user to database", 
    "Query execution was interrupted", "Out of range value for column",     "Invalid connection string", "MySQL server has gone away (packet bigger than max allowed size)", 
    "Invalid data type for column", "Check constraint violation", "Can't drop database", 
    "Table already exists in the database", "Cannot update table",     "Lost connection to MySQL server during query", "Too many joins", "Unknown error", 
    "No matching row in the table"
    
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

database_error_regex = re.compile(r"(" + "|".join(map(re.escape, database_error)) + r")", re.IGNORECASE)
network_error_regex = re.compile(r"(" + "|".join(map(re.escape, network_error)) + r")", re.IGNORECASE)
authentication_error_regex = re.compile(r"(" + "|".join(map(re.escape, authentication_error)) + r")", re.IGNORECASE)
configuration_error_regex = re.compile(r"(" + "|".join(map(re.escape, configuration_error)) + r")", re.IGNORECASE)

query = "SELECT timestamp, source, message FROM logs"
logs_df = pd.read_sql(query, engine)

logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)

def logs(request):
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)
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
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)
    if logs_df['timestamp'].isnull().any():
        print("Invalid timestamps found. Dropping these rows.")
        logs_df = logs_df.dropna(subset=['timestamp'])
        
#############all sources that contibute log##########
    #error_logs = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]
    top_sources = logs_df['source'].value_counts().head(10).reset_index()
    top_sources.columns = ['Source', 'Log Count']
    
    fig = px.bar(
    top_sources,
    x='Source',
    y='Log Count',
    title='Top 10 Sources Contributing to Logs',
    text='Log Count',
    color='Source',
    color_continuous_scale='Blues'
         )
    fig.update_layout(
    title_font_size=18,
    xaxis_title='Source',
    yaxis_title='Number of Logs',
    xaxis_tickangle=45
)
    top_sources = logs_df['source'].value_counts().head(10)

    fig = go.Figure(
        data=[go.Bar(x=top_sources.index, y=top_sources.values, marker=dict(color='skyblue'))],
        layout=go.Layout(
            title='Top 10 Sources Contributing to Logs',
            xaxis=dict(title='Source'),
            yaxis=dict(title='Number of Logs'),
        ),
    )

    plot_div = pio.to_html(fig, full_html=False)
    


#########################################################################################################








    def categorize_error(message):
        
        message_lower = str(message).lower()
        """Function to categorize error messages based on keywords."""
        
       
        if any(db_error.lower() in message_lower for db_error in network_error):
            return 'NetworkError'
        elif any(db_error.lower() in message_lower for db_error in database_error):
            return 'DatabaseError'
        elif any(db_error.lower() in message_lower for db_error in configuration_error):
            return 'ConfigurationError'
        elif any(db_error.lower() in message_lower for db_error in authentication_error):
            return 'AuthenticationError'      
        else:
            return 'GeneralError'''

    
        
    logs_df['error_category'] = logs_df['message'].apply(categorize_error)
    error_counts = logs_df['error_category'].value_counts()
    ##########################################################################################
    #                                                                                        #
    #                                Error Category                                          #
    #                                                                                        #
    ##########################################################################################
    fig = go.Figure(data=[go.Bar(
    x=error_counts.index,  # Error categories
    y=error_counts.values,  # Frequency of each error category
    marker=dict(color='skyblue'),
    )])

    # Update the layout of the chart
    fig.update_layout(
        title="Error  Category",
        xaxis_title="Error Type",
        yaxis_title="Frequency",
        xaxis_tickangle=45,
        plot_bgcolor='white',  # Set plot background to white
        paper_bgcolor='white',  # Set entire figure background to white
        title_font_size=18,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        margin=dict(l=50, r=50, t=50, b=50)
    )


    # Convert the Plotly figure to HTML for embedding or rendering in your template
    error_cat = pio.to_html(fig, full_html=False)
    
    
    ##########################################################################################
    #                                                                                        #
    #                                log contibution for error                               #
    #                                                                                        #
    ##########################################################################################
    
    
    
    def contains_error_type(message):
        """Check if a message contains any error keyword from the predefined sets."""
        message_lower = str(message).lower()
        if any(error.lower() in message_lower for error in database_error.union(network_error, authentication_error, configuration_error)):
            return True
        return False

    # Filter the DataFrame for rows that contain errors
    error_logs = logs_df[logs_df['message'].apply(contains_error_type)]

    # Count the number of errors per source
    errors_per_source = error_logs['source'].value_counts().head(10)

    # Create a bar chart for errors per source
    fig = go.Figure(
        data=[go.Bar(x=errors_per_source.index, y=errors_per_source.values, marker=dict(color='skyblue'))],
        layout=go.Layout(
            title='Top 10 Sources Contributing to Errors',
            xaxis=dict(title='Source'),
            yaxis=dict(title='Number of Errors'),
            xaxis_tickangle=-45
        ),
    )

    # Convert the Plotly figure to HTML for rendering in the template
    plot_div_source_errors = pio.to_html(fig, full_html=False)

    ##########################################################################################
    #                                                                                        #
    #                       Error category in pie-chart                                      #
    #                                                                                        #
    ##########################################################################################
    
    fig = go.Figure(data=[go.Pie(
    labels=error_counts.index,  # Error categories
    values=error_counts.values,  # Frequency of each error category
    marker=dict(colors=['skyblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightgray']),
    hole=0.3  # Create a donut chart effect
    )])

    # Update the layout of the pie chart
    fig.update_layout(
        title="Error Categories Distribution",
        title_font_size=18,
        plot_bgcolor='white',  # Set plot background to white
        paper_bgcolor='white',  # Set entire figure background to white
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # Convert the figure to HTML for embedding or rendering in your template
    pie_chart_html = pio.to_html(fig, full_html=False)
   
    database_error_count = len(logs_df[logs_df['error_category'] == 'DatabaseError'])
    network_error_count = len(logs_df[logs_df['error_category'] == 'NetworkError'])
    Auth_count = len(logs_df[logs_df['error_category'] == 'AuthenticationError'])
    general_count = len(logs_df[logs_df['error_category'] == 'GeneralError'])
    config_count = len(logs_df[logs_df['error_category'] == 'ConfigurationError'])
    client_count = len(logs_df[logs_df['error_category'] == 'ClientSideIssue'])


    ##########################################################################################
    #                                                                                        #
    #                        Hourly Frequency of error logs                                  #
    #                                                                                        #
    ##########################################################################################
                        
    def categorizee_error(message):
        
        message_lower = str(message).lower()
        """Function to categorize error messages based on keywords."""
        
       
        if any(db_error.lower() in message_lower for db_error in network_error):
            return 'NetworkError'
        elif any(db_error.lower() in message_lower for db_error in database_error):
            return 'DatabaseError'
        elif any(db_error.lower() in message_lower for db_error in configuration_error):
            return 'ConfigurationError'
        elif any(db_error.lower() in message_lower for db_error in authentication_error):
            return 'AuthenticationError'      
        else:
            return 'GeneralError'''

    
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)

    # Convert the 'timestamp' column to datetime

    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)

    # Filter only logs containing the word 'error'

    # Add a category column
    logs_df['category'] = logs_df['message'].apply(categorizee_error)

# Debug: Check if all categories are being recognized
    print("Category counts:")
    print(logs_df['category'].value_counts())

    # Filter logs with valid categories (optional: exclude GeneralError if desired)
    categorized_logs_df = logs_df

    # Group by day, hour, and category
    categorized_logs_df['day_hour'] = categorized_logs_df['timestamp'].dt.strftime('%Y-%m-%d %I:%M %p')
    error_trends = categorized_logs_df.groupby(['day_hour', 'category']).size().unstack(fill_value=0)

    # Debug: Check the grouped data
    print("Grouped data:")
    print(error_trends.head())

    # Create the Plotly figure
    fig = go.Figure()

    for category in error_trends.columns:
        fig.add_trace(go.Scatter(
            x=error_trends.index,
            y=error_trends[category],
            mode='lines+markers',
            name=category
        ))

    # Update the layout
    fig.update_layout(
        title="Error Trends by Day and Hour (Categorized)",
        xaxis=dict(title="Date and Hour", tickangle=45),
        yaxis=dict(title="Error Count"),
        showlegend=True,
        template="plotly_dark"
    )

    # Check raw counts

    



    # Convert the Plotly figure to HTML for embedding or rendering in your template
    plot_html = pio.to_html(fig, full_html=False)
    ##########################################################################################
    #                                                                                        #
    #                            Severity Distribution                                       #
    #                                                                                        #
    ##########################################################################################
    severity_keywords = {
        "Critical": ["critical", "fatal", "emergency"],
        "High": ["high", "severe", "major"],
        "Medium": ["medium", "moderate", "warning"],
        "Low": ["low", "minor", "info", "notice"]
    }   

    def categorize_severity(message):
        message_lower = str(message).lower()
        for level, keywords in severity_keywords.items():
            if any(keyword.lower() in message_lower for keyword in keywords):
                return level
        return "Unknown"  # Default if no keywords match

    logs_df['severity'] = logs_df['message'].apply(categorize_severity)
    severity_counts = logs_df['severity'].value_counts()

    fig_severity = go.Figure(
        data=[go.Bar(
            x=severity_counts.index, 
            y=severity_counts.values, 
            marker=dict(color=['red', 'orange', 'yellow', 'green', 'gray']),
            text=severity_counts.values, 
            textposition='outside', 
            hoverinfo='x+y+text'
        )],
        layout=go.Layout(
            title="Log Distribution by Severity Level",
            title_x=0.5,
            title_font_size=16,
            xaxis_title="Severity Level",
            yaxis_title="Number of Logs",
            xaxis=dict(tickangle=45),
            margin=dict(l=0, r=0, t=50, b=50)
        ),
    )
    plot_div_severity = pio.to_html(fig_severity, full_html=False)



    context = {
        
        'plot_image': 'images/error_types_plot.png',
        'error_types_plot': 'images/error_types.png',  # Path to the saved plot
        'database_error_count': database_error_count,
        'network_error_count' : network_error_count,
        'Auth_count' : Auth_count,
        'general_count' :general_count,
        'config_count' :config_count,
        'client_count': client_count,
        'ip_error_plot' : 'images/ip_error_plot.png',
        'plot_div': plot_div,
        'plot_div_source_errors':plot_div_source_errors,
        'severity_counts' : severity_counts,
        'top_sources_plot': 'images/top10.png',
        'top_error_sources': 'images/toperror.png',
        'severity': 'images/severity.png',
        'error_frequency_plot': 'images/error_frequency.png',
        'severity_image': 'images/severity_distribution.png',
        'source_image': 'images/error_sources.png',
        'hourly_errorr':'images/hourly_error.png',
        'serverity_plot':'images/severity_chart.png',
        'plot_div_severity':plot_div_severity,
        'plot_html':plot_html,
        'error_cat': error_cat,
        'pie_chart_html':pie_chart_html,
        #'plot_div_error_frequency':plot_div_error_frequency,
       
    }
    
    return render(request, 'temp/show.html', context)

def errorcategory(request):
    query = "SELECT * FROM logs"
    logs_df = pd.read_sql(query, con=engine)
    def categorize_error(message):
        message_lower = str(message).lower()
        """Function to categorize error messages based on keywords."""
        
        if any(db_error.lower() in message_lower for db_error in network_error):
            return 'NetworkError'
        elif any(db_error.lower() in message_lower for db_error in database_error):
            return 'DatabaseError'
        elif any(db_error.lower() in message_lower for db_error in configuration_error):
            return 'ConfigurationError'
        elif any(db_error.lower() in message_lower for db_error in authentication_error):
            return 'AuthenticationError'      
        else:
            return 'GeneralError'
    logs_df['error_category'] = logs_df['message'].apply(categorize_error)

    # Count errors by category
    database_error_count = len(logs_df[logs_df['error_category'] == 'DatabaseError'])
    network_error_count = len(logs_df[logs_df['error_category'] == 'NetworkError'])
    auth_count = len(logs_df[logs_df['error_category'] == 'AuthenticationError'])
    general_count = len(logs_df[logs_df['error_category'] == 'GeneralError'])
    config_count = len(logs_df[logs_df['error_category'] == 'ConfigurationError'])
    client_count = len(logs_df[logs_df['error_category'] == '404badrequest'])

    total = (database_error_count + network_error_count + auth_count +
             general_count + config_count + client_count)

    # Top error messages
    mylog = logs_df[logs_df['message'].str.contains('error', case=False, na=False)]
    top_error_messages = mylog['message'].value_counts().head(10).to_dict()

    # Error occurrences for chart
    error_counts = logs_df['error_category'].value_counts()
    context = {
        'error_counts': error_counts.to_dict(),
        'database_error_count': database_error_count,
        'network_error_count': network_error_count,
        'auth_count': auth_count,
        'general_count': general_count,
        'config_count': config_count,
        'client_count': client_count,
        'top_error_messages': top_error_messages,
        'total': total,
    }
    
    

    # Return the response with data to the template
    return render(request, 'temp/errorcategory.html', context)

def network(request):
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)

    if logs_df['timestamp'].isnull().any():
        print("Invalid timestamps found. Dropping these rows.")
        logs_df = logs_df.dropna(subset=['timestamp'])
    
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)

    def categorize_error(message):
        message_lower = str(message).lower()  # Ensure the message is a string and convert it to lowercase
        if any(db_error.lower() in message_lower for db_error in network_error):
            return 'NetworkError'
        else:
            pass
 
    logs_df['error_type'] = logs_df['message'].apply(categorize_error)
    network_error_logs = logs_df[logs_df['error_type'] == 'NetworkError']
    cnt = len(network_error_logs)

    context = {
        'network_error_logs': network_error_logs,
        'cnt' : cnt
    }
    

    
    return render(request, 'temp/network.html', context)

def database(request):
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)
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
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)
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
    logs_df['message'] = logs_df['message'].fillna('').astype(str)
    
    general_error_logs = logs_df[logs_df['message'].apply(lambda msg: categorize_error(msg) == 'GeneralError')]
    general_error_logs['formatted_timestamp'] = general_error_logs['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    
    cnt = len(general_error_logs)

    context = {'general_error_logs': general_error_logs,
               'cnt' : cnt
               
               
               }
    return render(request, 'temp/general.html', context)

def auth(request):

    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)    
    # Ensure timestamp is properly formatted
    
    if logs_df['timestamp'].isnull().any():
        print("Invalid timestamps found. Dropping these rows.")
        logs_df = logs_df.dropna(subset=['timestamp'])
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)
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


    
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)    
    # Ensure timestamp is properly formatted
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
    if logs_df['timestamp'].isnull().any():
        print("Invalid timestamps found. Dropping these rows.")
        logs_df = logs_df.dropna(subset=['timestamp'])
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)

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
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)    
    # Ensure timestamp is properly formatted
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
    if logs_df['timestamp'].isnull().any():
        logs_df = logs_df.dropna(subset=['timestamp'])
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)

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
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)
    source_counts = logs_df['source'].value_counts()    
    top_sources = source_counts.head(10)

    context = {

        'top_sources': top_sources,

        
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

def export_error_logs_csv(request, error_type):
    # Read the logs CSV (or use the already filtered logs if they are passed in context)
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)
    # Ensure the timestamp column is correctly parsed and localized
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce', utc=True)
    logs_df['timestamp'] = logs_df['timestamp'].dt.tz_convert('Africa/Addis_Ababa').dt.tz_localize(None)

    # Categorize the errors
    def categorize_error(message):
        message_lower = str(message).lower()
        if any(db_error.lower() in message_lower for db_error in network_error):
            return 'NetworkError'
        elif any(db_error.lower() in message_lower for db_error in database_error):
            return 'DatabaseError'
        elif any(db_error.lower() in message_lower for db_error in authentication_error):
            return 'AuthenticationError'
        elif any(db_error.lower() in message_lower for db_error in configuration_error):
            return 'ConfigurationError'
        else:
            return 'GeneralError'

    # Apply the categorization function to each log message
    logs_df['error_type'] = logs_df['message'].apply(categorize_error)

    # Filter the logs based on the requested error category
    error_logs = logs_df[logs_df['error_type'] == error_type]


    # Convert to list of dicts for CSV export
    logs = error_logs.to_dict('records')


    if not logs:
        return HttpResponse(f"No {error_type} logs to export.", status=400)

    # Create a response object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{error_type}_logs.csv"'

    # Write data to CSV
    writer = csv.writer(response)

    # Write the header (column names) correctly as a list
    writer.writerow(error_logs.columns.to_list())  # Convert columns to a list

    # Write data rows
    for log in logs:
        writer.writerow(log.values())  # Write each log entry's values

    return response

def export_all_logs_csv(request):
    # Read the entire logs DataFrame
    query = "SELECT timestamp, source, message FROM logs"
    logs_df = pd.read_sql(query, engine)    
    # Create a response object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_logs.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write the header (column names)
    writer.writerow(logs_df.columns)
    
    # Write data rows
    for log in logs_df.itertuples(index=False, name=None):  # Efficient way to iterate through rows
        writer.writerow(log)
    
    return response