# Required libraries
import os
import locale
import requests
import pandas as pd
import requests_html

from datetime import datetime as dt
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to update daily cumulative administered vaccines
def get_new_data():
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

    link = 'https://vacunate.gob.do/'

    retry_strategy = Retry(
        total = 3,
        status_forcelist = [408, 429, 500, 502, 503, 504],
        method_whitelist = ["HEAD", "GET", "OPTIONS"])
    
    adapter = HTTPAdapter(max_retries = retry_strategy)

    session = requests_html.HTMLSession()
    session.mount("https://", adapter)
    r = session.get(link)
    r.html.render(sleep=5, timeout=8)

    # Extracting date and doses administered
    date = r.html.xpath('/html/body/div/div/section[2]/div/div[1]/h3/span/text()')[0]
    dose_1 = r.html.xpath('/html/body/div/div/section[2]/div/div[1]/div/div[1]/div[1]/text()')[0]
    dose_2 = r.html.xpath('/html/body/div/div/section[2]/div/div[1]/div/div[2]/div[1]/text()')[0]
    dose_3 = r.html.xpath('/html/body/div/div/section[2]/div/div[1]/div/div[3]/div[1]/text()')[0]
    dose_total = r.html.xpath('/html/body/div/div/section[2]/div/div[1]/div/div[4]/div[1]/text()')[0]
    
    session.close()
    r.close()

    # Formatting date
    date = date.replace('| Acumulados al', '').strip()
    date = dt.strptime(date, '%d de %B de %Y')

    # Formatting numbers
    dose_1 = int(dose_1.replace(',', '').strip())
    dose_2 = int(dose_2.replace(',', '').strip())
    dose_3 = int(dose_3.replace(',', '').strip())
    dose_total = int(dose_total.replace(',', '').strip())

    # Creating DataFrame with new data
    new_data = pd.DataFrame(data = {
        'date' : [date],
        'dose_1' : [dose_1],
        'dose_2' : [dose_2],
        'dose_3' : [dose_3],
        'dose_total' : [dose_total]})
    
    return new_data

# Creating DataFrame with new data
new_data = get_new_data()

# Importing base DataFrame
old_data = pd.read_csv('./2_data/vaccines.csv')
old_data['date'] = pd.to_datetime(old_data['date'])

# Comapring new_date against old_date
old_date = old_data['date'].max()
new_date = new_data['date'].max()

if(new_date > old_date):
    print("\nNew data:")
    print(new_data.head())
    print("\n")
    
    # Merging and exporting complete vaccination data
    vaccines = pd.concat([old_data, new_data])
    vaccines.to_csv('./2_data/vaccines.csv', index = 0)
    
    print('Updates done.')
else:
    print('No new data available.')

input("Press any button to finish.")