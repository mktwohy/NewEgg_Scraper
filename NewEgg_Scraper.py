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
        
def pickle_data(filename = 'PickledData'):
    filename = filename+"%s"+'.pickle'
    i = 0
    while exists(filename % i):
        i += 1
    with open(filename % i,'wb') as file:
        file.write(pickle.dumps(data))    

def get_soup(url):
        uClient = uReq(url.replace(' ','')) # opening up connection
        page_html = uClient.read() # grabbing the page
        uClient.close() # closing connection
        
        return bSoup(page_html, "html.parser") # parse html
    
def scrape_page(page_url):
    p = Page(page_url)  # Create page object, which then adds products to list  

    if p.page_number < p.last_page_number:
        scrape_page(p.next_page_url)
    
#TODO
def save_as_csv(filename = 'newEgg_Scrape'):
        pass
    
def main():
    scrape_page('https://www.newegg.com/p/pl?d=laptop&N=4113%204112')
    # print(data)
    pickle_data()
    
    
#TODO
class Page:
    def __init__(self, page_url):
        self.url = page_url
        self.soup = get_soup(page_url)
        self.page_number, self.last_page_number = self.scrape_page_num()
        self.next_page_url = self.scrape_next_page_url()
        self.scrape_products()
        print(self.page_number)
        
   
    """Returns list of current page number and last page number"""
    def scrape_page_num(self):
        pagination = self.soup.findAll("span",{"class":"list-tool-pagination-text"}) 
        str_list = pagination[0].text.split()[1].split('/')
        int_list = list(map(int,str_list))
        return int_list
    
    def scrape_next_page_url(self):
        if self.page_number == self.last_page_number:
            return None
        if '&' in self.url:
            self.url = self.url.split('&')[0] #remove &page#
        new_url = self.url + "&page=" + str(self.page_number+1)
        return new_url
    
    """creates a Product object for every product on the page"""
    def scrape_products(self):
        containers = self.soup.find_all("div",{"class":"item-container"})
        for c in containers:
            try:
                product_url = c.a['href']
                Product(product_url) 
                print("Added Product")
                sleep(random.randint(2, 10))
            except: 
                print("Fail")
    
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




    
if __name__=="__main__":
    main()

