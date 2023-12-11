import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# General function to scrape data from a table
# Start by making sure you can connect and find the table, then, if possible, return the table
def scrape_table(session, url):
    try:
        response = session.get(url)
        response.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
        return pd.DataFrame()
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return pd.DataFrame()
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return pd.DataFrame()
    except requests.exceptions.RequestException as err:
        print("Error:", err)
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if table is not None:
        data = pd.read_html(str(table))
        
        # Extract conference and year from the URL
        conference = url.split('/')[-2].upper()
        year = (url.split('/')[-1])
        year = int(year.split("-")[0])
        
        # Add conference and year columns to our extracted data
        # MIGHT WANT TO CHANGE THIS IF YOU ARE NOT DOING COLLEGE WORK
        data[0]['Conference'] = conference
        data[0]['Year'] = year
        
        return data[0]
    else:
        print(f"No table found on {url}")
        return pd.DataFrame()

# List of URLs - uses formatted strings to iterate through all the years I want to look at
urls = []
for i in range(2014, 2024):
    url = f"https://www.sports-reference.com/cfb/conferences/pac-12/{i}-ratings.html"
    urls.append(url)
    url = f"https://www.sports-reference.com/cfb/conferences/acc/{i}-ratings.html"
    urls.append(url)
    url = f"https://www.sports-reference.com/cfb/conferences/big-12/{i}-ratings.html"
    urls.append(url)
    url = f"https://www.sports-reference.com/cfb/conferences/big-ten/{i}-ratings.html"
    urls.append(url)
    url = f"https://www.sports-reference.com/cfb/conferences/sec/{i}-ratings.html"
    urls.append(url)


# Counter for request tracking - do this to also avoid rate limiting
request_counter = 0

# Maximum requests before creating a new session
max_requests_before_new_session = 15

combined_data = pd.DataFrame()

# Create a session
session = requests.Session()

for url in urls:
    print("Processing URL:", url)

    # Scrape the data from the table at the given URL, then add it to our overarching dataframe
    table_data = scrape_table(session, url)
    combined_data = pd.concat([combined_data, table_data], ignore_index=True)
    
    request_counter += 1
    
    # Check if it's time to create a new session; if it is, then do so
    if request_counter >= max_requests_before_new_session:
        session.close() 
        session = requests.Session()  
        request_counter = 0  
    
    # Introduce a delay of 3.01 seconds to avoid making 20+ requests per minute
    time.sleep(3.01)

# Save the combined data to a CSV file to process it further in R
combined_data.to_csv('cfb_p5_adv_data.csv', index=False)
