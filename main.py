# Module Imports
import drive as drive
from bs4 import BeautifulSoup
import urllib
import re
from selenium import webdriver
import numpy as np
import pandas as pd
from selenium.common.exceptions import TimeoutException
import requests
from tqdm import tqdm
import time
import locale

# Setting up Chromium and Webdriver
option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome(options=option)  # just to make sure that codes won't open browser automatically lol
# driver = webdriver.Chrome() #use this if you wanna see the browser in action, and waste battery power

html_page = urllib.request.urlopen('https://www.forbes.com/sites/forbesfinancecouncil/archive/2021/05/')
soup = BeautifulSoup(html_page)

df = pd.DataFrame(columns=['link'])

for link in soup.findAll('a'):
    try:
        if 'forbesfinancecouncil/2021' in link.get('href'):
            df = df.append({'link': link.get('href')}, ignore_index=True)
        else:
            pass
    except:
        pass

df.drop_duplicates(subset="link", keep=False, inplace=True)
df.reset_index(drop=True, inplace=True)


def get_views(row):
    links = row['link']
    try:
        driver.get(links)
    except TimeoutException:
        driver.execute_script("window.stop();")
    try:
        views = driver.find_element_by_class_name('pageviews')
        return views.text.split()[0]
    except:
        return 'NA'


driver.set_page_load_timeout(3)  # this sets the time-out to just 3 seconds

df['views'] = df.apply(lambda row: get_views(row), axis=1)

driver.set_page_load_timeout(3)
# driver = webdriver.Chrome(options=option)
driver = webdriver.Chrome()

for index in df[df['views'] == 'NA'].index:
    link = df.loc[index, 'link']
    try:
        driver.get(link)
        print('Link {} grabbed.'.format(index))
    except TimeoutException:
        driver.execute_script("window.stop();")
        print('Link {} failed grab.'.format(index))
        print(link)
    try:
        views = driver.find_element_by_class_name('pageviews')
        df.loc[index, 'views'] = views.text.split()[0]
        print('Views of link {} collected.'.format(index))
    except:
        print('Link {} failed views collection.'.format(index))
        print(link)
        driver.refresh()
    if (df.loc[index, 'views'] == 'NA') and (df.loc[index - 1, 'views'] == 'NA'):
        # driver = webdriver.Chrome(options=option)
        driver.close()
        driver = webdriver.Chrome()
    else:
        pass


def get_title(row):
    link = row['link']
    try:
        driver.get(link)
    except TimeoutException:
        driver.execute_script("window.stop();")
    try:
        return driver.title
    except:
        return 'NA'


driver.set_page_load_timeout(3)  # this sets the time-out to just 3 seconds

df['title'] = df.apply(lambda row: get_title(row), axis=1)

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

for index in df.index:
    if type(df.loc[index, 'views']) == int:
        pass
    else:
        if ',' in df.loc[index, 'views']:
            df.loc[index, 'views'] = int(locale.atoi(df.loc[index, 'views']))
        else:
            df.loc[index, 'views'] = int(df.loc[index, 'views'])

df.sort_values(by="views", ascending=False, inplace=True)

df.to_csv('FlavourOfTheMonth.csv')

driver.close()

print('Code ran successfully. Enjoy the Flavour of the Month :)')
