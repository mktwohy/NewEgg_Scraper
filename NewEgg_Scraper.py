# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 00:48:50 2021

@author: Twohy
"""


from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from time import sleep
import random

product_specs = []

class product():
    def __init__(self, spec_list):
        self.spec_list = spec_list
        self.model
        self.brand
        self.cpu

def get_soup(url):
    #opening up connection, grabbing the page
    uClient = uReq(url.replace(' ',''))
    page_html = uClient.read() # raw html
    uClient.close()
    
    # html parsing
    return soup(page_html, "html.parser") # parsed html


def save_html_data(soup):
    containers = soup.find_all("div",{"class":"item-container"})
    numFail = 0
    for c in containers:
        try:
            product_url = c.a['href']
            details = get_product_data(product_url)
            print(details)
            sleep(random.randint(2, 10))
            product_specs.append(product(details))

            
            
        except: 
            numFail += 1
            
    print(numFail,"failed out of",len(containers))

"""Returns list of current page number and last page number"""
def get_page_num(soup):
    pagination = soup.findAll("span",{"class":"list-tool-pagination-text"}) 
    str_list = pagination[0].text.split()[1].split('/')
    int_list = list(map(int,str_list))
    return int_list



def next_page_url(current_url, current_page_num):
    if '&' in current_url:
        current_url = current_url.split('&')[0] #remove &page#
    print(current_page_num)
    new_url = current_url + "&page=" + str(current_page_num+1)
    print(new_url)
    return new_url
            


def save_as_csv(filename):
    f = open(filename, "w")
    headers = "brand, product_name, shipping\n"
    f.write(headers)
    for i in range(len(brands)):
        f.write(brands[i] +","+ product_names[i].replace(",","|") +","+ shipping_costs[i]+ "\n")

    f.close()
    
def get_product_data(url):
    product_soup = get_soup(url.replace(' ',''))
    # details = soup.find_all("div",{'id':'product-details'})
    tables = product_soup.find_all("table",{'class':'table-horizontal'})
    rows = list()
    for i in range(len(tables)):
        for row in tables[i].findAll("tr"):
            rows.append(row)
    
    for i in range(len(rows)):
        rows[i] = rows[i].th.text, rows[i].td.text
    return rows

def scrape(page_url):
    page_html = get_soup(page_url)
    page_num, last_page_num = get_page_num(page_html)
    save_html_data(page_html)
    
    if page_num < 3: #last_page_num
        sleep(random.randint(2, 10))
        scrape(next_page_url(page_url, page_num))


# site URLs
gtx_url = 'https://www.newegg.com/p/pl?d=gtx+1050&page=2'
laptop_url = 'https://www.newegg.com/p/pl?d=laptop' 
xps15_url = 'https://www.newegg.com/p/pl?d=dell+xps+15'
xps15_product_url = 'https://www.newegg.com/p/1TS-000A-0BMX1?Description=dell xps 15&cm_re=dell_xps 15-_-1TS-000A-0BMX1-_-Product'
        
scrape(gtx_url)
# save_as_csv("laptops.csv")

