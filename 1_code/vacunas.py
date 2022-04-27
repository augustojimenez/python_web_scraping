# Required libraries
import os
import pandas as pd
import locale

from time import sleep
from datetime import datetime as dt
from selenium import webdriver

# Project directory
os.chdir(r'C:\Users\Augus\OneDrive\Documents\Proyectos\Python Web Scraping - Vaccines')

# Function to update daily cumulative administered vaccines
def get_new_data(sleep_time = 0):
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

    link = 'https://vacunate.gob.do/'

    opts = webdriver.ChromeOptions()
    #opts.headless = True

    driver = webdriver.Chrome(executable_path = r'C:\Users\Augus\OneDrive\Documents\Proyectos\Python Web Scraping - Vaccines\driver\chromedriver.exe', options = opts)
    sleep(sleep_time)
    
    # Extracting date and doses administered
    try:
        driver.get(link)
        sleep(sleep_time)
        fecha = driver.find_element_by_xpath('/html/body/div/div/section[2]/div/div[1]/h3/span').text
        fecha = driver.find_element_by_xpath('//*[@id="root"]/section[2]/div/div[1]/h5').text
        dosis_1 = driver.find_element_by_xpath('//*[@id="root"]/section[2]/div/div[2]/div/div[1]/div/div/span').text
        dosis_2 = driver.find_element_by_xpath('//*[@id="root"]/section[2]/div/div[2]/div/div[2]/div/div/span').text
        dosis_3 = driver.find_element_by_xpath('//*[@id="root"]/section[2]/div/div[2]/div/div[3]/div/div/span').text
        dosis_total = driver.find_element_by_xpath('//*[@id="root"]/section[2]/div/div[2]/div/div[4]/div/div/span').text
    except:
        driver.close()
        return None

    driver.close()

    # Formatting date
    fecha = fecha.replace('Acumulados al', '').strip()
    fecha = fecha.replace(' de', '').strip()
    fecha = dt.strptime(fecha, '%d %B %Y')

    # Formatting numbers
    dosis_1 = int(dosis_1.replace(',', '').strip())
    dosis_2 = int(dosis_2.replace(',', '').strip())
    dosis_3 = int(dosis_3.replace(',', '').strip())
    dosis_total = int(dosis_total.replace(',', '').strip())

    # Creating DataFrame with new data
    new_data = pd.DataFrame(data = {
        'fecha' : [fecha],
        'dosis_1' : [dosis_1],
        'dosis_2' : [dosis_2],
        'dosis_3' : [dosis_3],
        'dosis_total' : [dosis_total]})
    
    return new_data

# Creating DataFrame with new data
is_none = True
n = 0
while is_none:
    print(str(n) + " try.")
    new_data = get_new_data(sleep_time = n)
    if (n < 10):
        n = n + 1
        is_none = new_data is None
    else:
        is_none = False

# Importing base DataFrame
old_data = pd.read_csv('./2_data/vacunas.csv')
old_data['fecha'] = pd.to_datetime(old_data['fecha'])

# Comapring new_date against old_date
old_date = old_data['fecha'].max()
new_date = new_data['fecha'].max()

if(new_date > old_date):
    print("\n Nueva data:")
    print(new_data.head())
    print("\n")
    
    # Merging and exporting complete vaccination data
    vacunas = pd.concat([old_data, new_data])
    vacunas.to_csv('./2_data/vacunas.csv', index = 0)
    
    print('Actualización realizada.')
else:
    print('No hay nuevos datos para actualizar.')

input("Presione cualquier tecla para terminar.")