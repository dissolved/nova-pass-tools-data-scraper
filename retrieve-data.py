import requests
import json
from datetime import datetime, timedelta

# Define the URLs
TOOLS_API_URL = "https://np.nova-labs.org/stats/tools"
SESSIONS_API_URL = "https://np.nova-labs.org/stats/tool-sessions"
EARLIEST_DATE = datetime(2020, 1, 27).date()

# Function to get the list of tools
def fetch_tools():
    response = requests.get(TOOLS_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch tools: HTTP {response.status_code}")

# Function to get data for a given tool and date range
def fetch_tool_data(tool_id, start_time, end_time):
    params = {
        "tool_id": tool_id,
        "start_time": start_time,
        "end_time": end_time
    }
    response = requests.get(SESSIONS_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data for tool {tool_id}: HTTP{response.status_code}")


# Function to summarize session count and hours of use
def summarize_tool_data(tool_id, data):
    session_count = len(data)
    hours_of_use = sum(parse_duration(session['duration']) for session in data)
    
    return {
        "tool_id": tool_id,
        "session_count": session_count,
        "hours_of_use": hours_of_use
    }

def parse_duration(duration_str):
    hours, minutes, seconds = duration_str.split(':')
    return int(hours) + int(minutes) / 60 + float(seconds) / 3600

# Function to aggregate data for each tool on a monthly basis
def get_monthly_data(tools):
    monthly_data = []
    
    # Loop through each month in the range
    start_date = end_date =datetime.now().date()
    while end_date > EARLIEST_DATE:
        start_date, end_date = get_previous_month_start_end_date(start_date)

        print(f"Fetching data for {start_date} - {end_date}")
        # Fetch and summarize data for each tool
        for tool in tools:
            try:
                tool_data = fetch_tool_data(tool['id'], start_date, end_date)
                summary = summarize_tool_data(tool['id'], tool_data)
                monthly_data.append({
                    "month": start_date.strftime('%Y-%m'),
                    "tool_id": tool['id'],
                    "tool_name": tool['name'],
                    "session_count": summary['session_count'],
                    "hours_of_use": summary['hours_of_use']
                })
            except Exception as e:
                print(f"An error occurred: {e}")
    return monthly_data

def get_previous_month_start_end_date(start_date):
    end_date_previous_month = start_date.replace(day=1) - timedelta(days=1)
    start_date_previous_month = end_date_previous_month.replace(day=1)
    return start_date_previous_month, end_date_previous_month

# Main script to aggregate data for a range of months
if __name__ == "__main__":
    monthly_data = []

    try:
        # Step 1: Fetch the list of tools
        tools = fetch_tools()
    
        # Step 2: Get and print the monthly data summary
        monthly_data = get_monthly_data(tools)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        print(json.dumps(monthly_data, indent=2))
