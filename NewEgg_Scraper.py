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
htmls = list()
page_limit = 100

def pickle_data(data_to_pickle, filename = 'PickledData'):
    filename = filename+"%s"+'.pickle'
    i = 0
    while exists(filename % i):
        i += 1
    with open(filename % i,'wb') as file:
        file.write(pickle.dumps(data_to_pickle))
    print(filename % i,'pickled!')

def get_soup(url):
        # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        uClient = uReq(url.replace(' ','')) # opening up connection
        page_html = uClient.read() # grabbing the page
        uClient.close() # closing connection
        
        return bSoup(page_html, "html.parser") # parse html

def load_pickle(filename):
    with open(filename+'.pickle', 'rb') as file:
        p = pickle.load(file)
    return p

def pickle_to_soup(html):
    return bSoup(html, "html.parser")

def get_html(url):
    uClient = uReq(url.replace(' ','')) # opening up connection
    page_html = uClient.read() # grabbing the page
    uClient.close() # closing connection
        
    return page_html
    
def scrape_page(page_url):
    p = Page(page_url)  # Create page object, which then adds products to list  

    if p.page_number < p.last_page_number and p.page_number < page_limit:
        scrape_page(p.next_page_url)
    
#TODO
def save_as_csv(filename = 'newEgg_Scrape'):
        pass
    
def main():
    scrape_page('https://www.newegg.com/p/pl?d=gtx+1050')
    # print(data)
    pickle_data(data)
    pickle_data(htmls)
    
    
#TODO
class Page:
    def __init__(self, page_url):
        self.url = page_url
        self.soup = get_soup(page_url)
        self.page_number, self.last_page_number = self.scrape_page_num()
        print("page",self.page_number,'out of',self.last_page_number)
        self.next_page_url = self.scrape_next_page_url()
        self.scrape_products()
        
   
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
        i = 1
        for c in containers:
            try:
                product_url = c.a['href']
                Product(product_url) 
                print("\tProduct",i)
            except: 
                print("Fail")
            sleep(random.randint(2, 5))
            i+=1

    
class Product:
    def __init__(self,product_url):
        htmls.append(get_html(product_url)) # save the html
        self.soup = get_soup(product_url)
        self.all_specs = dict()
        self.filtered_specs = dict()
            
    
        self.scrape_price()
        self.scrape_rating()
        self.scrape_table()
        self.filter_results()
        # print(self.__str__())
        
        data.append(self.all_specs) # save the specs
                            
    def scrape_table(self):
        tables = self.soup.find_all("table",{'class':'table-horizontal'})
        for i in range(len(tables)):
            for row in tables[i].findAll("tr"):
                key = row.th.text.strip()
                val = row.td.text.strip()
                self.all_specs[key] = val

    #TODO
    def scrape_rating(self):
        ratings_container = self.soup.find_all('div',{'class':'product-rating'})
        rating = 'NA'
        if len(ratings_container) > 0:
            for r in range(5):
                class_name = 'rating rating-%s' % (r+1) 
                rating_icon = ratings_container[0].findAll('i',{'class':class_name})
                if len(rating_icon) > 0:
                    rating = r+1
       
        self.all_specs['Rating'] = str(rating)

        # review_container = self.soup.find_all('span',{'title':'Read reviews...'})
        
        
    
    def scrape_price(self):
        cur_price = self.soup.find_all('li',{'class':'price-current'})[0].text
        was_price = self.soup.find_all('li',{'class':'price-was'})[0].text
        
        if len(was_price) > 0:
            price = was_price
        else:
            price = cur_price
            
        self.all_specs['Price'] = price

    def filter_results(self):
         wanted_specs = ('Brand','Model','Price','Rating','CPU')
         for s in wanted_specs:
             if s in self.all_specs:
                 self.filtered_specs[s] = self.all_specs[s]

    def __str__(self):
        s = ''
        for k in self.filtered_specs:
            s = s +'\n'+ k +': ' + self.all_specs[k]
        return s

    
if __name__=="__main__":
    try:
        main()
    except(KeyboardInterrupt):
        print("Ending scrape. Saving htmls and data...")
        pickle_data(data, filename = 'PickledSpecs')
        pickle_data(htmls, filename = 'PickledHTML')
    except():
        print("Something went wrong. Saving htmls and data...")
        pickle_data(data, filename = 'PickledSpecs_CRASH')
        pickle_data(htmls, filename = 'PickledHTML_CRASH')

# soup1 = get_pickled_soup(pickled_htmls[0])
#Product('https://www.newegg.com/amd-ryzen-5-3600/p/N82E16819113569?Item=N82E16819113569&cm_sp=Homepage_dailydeals-_-P0_19-113-569-_-03132021&quicklink=true')
