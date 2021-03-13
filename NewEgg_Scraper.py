# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 22:20:54 2021

@author: Twohy
"""


from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as bSoup
from time import sleep
import random
import pickle
from os.path import exists

data = list()
    # def __init__(self, newegg_url):
    #     self.init_soup = self.get_soup(newegg_url)
    #     self.products = list()
    #     self.page = self.Page('https://www.newegg.com/p/pl?d=laptops')
        
def get_soup(url):
        uClient = uReq(url.replace(' ','')) # opening up connection
        page_html = uClient.read() # grabbing the page
        uClient.close() # closing connection
        
        return bSoup(page_html, "html.parser") # parse html
    
    
def scrape_page(page_url):
        # add all products to list  
        # if page_has_next
            # scrape_page(next_page)
        pass
    
def save(filename = 'newEgg_Scrape'):
        pass
    
    
    
class Page:
    def __init__(self, page_url):
        self.soup = get_soup(page_url)
   
    def find_next_page():
        pass
        
    
class Product:
    def __init__(self,product_url):
        self.soup = get_soup(product_url)
        self.all_specs = dict()
        self.filtered_specs = dict()
        
        self.scrape_price()
        self.scrape_rating()
        self.scrape_table()
        self.filter_results()
        
        data.append(self.all_specs)
                            
    def scrape_table(self):
        tables = self.soup.find_all("table",{'class':'table-horizontal'})
        for i in range(len(tables)):
            for row in tables[i].findAll("tr"):
                key = row.th.text.strip()
                val = row.td.text.strip()
                self.all_specs[key] = val

    #TODO
    def scrape_rating(self):
        pass
    
    def scrape_price(self):
        cur_price = self.soup.find_all('li',{'class':'price-current'})[0].text
        was_price = self.soup.find_all('li',{'class':'price-was'})[0].text
        
        if len(was_price) > 0:
            price = was_price
        else:
            price = cur_price
            
        self.all_specs['Price'] = price

    def filter_results(self):
         wanted_specs = ('Brand','Model','Price','CPU')
         for s in wanted_specs:
             if s in self.all_specs:
                 self.filtered_specs[s] = self.all_specs[s]

    def __str__(self):
        s = ''
        for k in self.filtered_specs:
            s = s +'\n'+ k +': ' + self.all_specs[k]
        return s

def pickle_data(filename = 'PickledData'):
    filename = filename+"%s"+'.pickle'
    i = 0
    while exists(filename % i):
        i += 1
    with open(filename % i,'wb') as file:
        file.write(pickle.dumps(data))


plink = 'https://www.newegg.com/carbon-gray-kuu-yobook-workstation/p/1TS-00BK-00049?Item=9SIANGPDNT4057&Description=laptops&cm_re=laptops-_-9SIANGPDNT4057-_-Product&cm_sp=SP-_-444662-_-0-_-0-_-9SIANGPDNT4057-_-laptops-_-laptop-_-4'
p = Product(plink)
print(data)

pickle_data()

