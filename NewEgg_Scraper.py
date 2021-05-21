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

#URLS
notebooks_url = 'https://www.newegg.com/p/pl?N=100006740%204814&Order=3&page=1'
gaming_url = 'https://www.newegg.com/p/pl?N=100167732%204814&Order=3'
two_in_one_url = 'https://www.newegg.com/p/pl?N=100020039%204814&page=1'
chromebooks_url = 'https://www.newegg.com/p/pl?N=100167750%204814'
mobile_workstations_url = 'https://www.newegg.com/p/pl?N=100167751%204814'
touch_laptops_url = 'https://www.newegg.com/p/pl?Submit=ENE&IsNodeId=1&N=100006740%20600414170%204814'
surface_laptops_url = 'https://www.newegg.com/p/pl?N=100006740%20601298036%20601323358%20601346246%204814'
surface_book_url = 'https://www.newegg.com/p/pl?N=100020039%2050001149%20601186726%20601305863%204814'
surface_pro_url = 'https://www.newegg.com/p/pl?N=100020039%2050001149%20601294701%20601294702%20601299030%20601323355%204814'
surface_go_url = 'https://www.newegg.com/p/pl?N=100020039%2050001149%20601319791%204814'
macbook_url = 'https://www.newegg.com/p/pl?N=100017489%2050001759%204814&SpeTabStoreType=0&Manufactory=1759'

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

def url_to_soup(url):
        uClient = uReq(url.replace(' ','')) # opening up connection
        page_html = uClient.read() # grabbing the page
        uClient.close() # closing connection
        
        return bSoup(page_html, "html.parser") # parse html

def html_to_soup(html):
    return bSoup(html, "html.parser")

def load_pickle(filename):
    with open(filename+'.pickle', 'rb') as file:
        p = pickle.load(file)
    return p

def get_html(url):
    uClient = uReq(url.replace(' ','')) # opening up connection
    page_html = uClient.read() # grabbing the page
    uClient.close() # closing connection
        
    return page_html
    
def scrape_page(page_url):
    p = Page(page_url)  # Create page object, which then adds products to list  

    if p.page_number < p.last_page_number and p.page_number < page_limit:
        scrape_page(p.next_page_url)
    

class Page:
    def __init__(self, page_url):
        self.url = page_url
        self.soup = url_to_soup(page_url)
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
                print("\tProduct",i,'failed')
            sleep(random.randint(5, 7))
            i+=1

    
class Product:
    def __init__(self,product_url):
        htmls.append(get_html(product_url)) # save the html
        self.soup = url_to_soup(product_url)
        self.all_specs = dict()
        self.filtered_specs = dict()
            
    
        self.scrape_price()
        self.scrape_rating()
        self.scrape_table()
        # self.filter_results()
        # print(self.__str__())
        
        data.append(self.all_specs) # save the specs
                            
    def scrape_table(self):
        tables = self.soup.find_all("table",{'class':'table-horizontal'})
        for i in range(len(tables)):
            for row in tables[i].findAll("tr"):
                key = row.th.text.strip()
                val = row.td.text.strip()
                self.all_specs[key] = val

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
    
def main(url,genre):
    try:
        scrape_page(url)
        print('Done with',genre+'!')
    except(KeyboardInterrupt):
        print("Ending scrape.")
    except():
        print("Something went wrong.")
    print('Saving htmls and data...')
    pickle_data(data,"PickledSpecs"+'_'+genre)
    pickle_data(htmls,"Pickled_HTML"+'_'+genre)

    
if __name__=="__main__":
    # main(notebooks_url,'Notebook')
    # main(mobile_workstations_url, 'mobileWorkstation')
    # main(two_in_one_url,'2in1_')
    # main(gaming_url,'gaming')
    # main(chromebooks_url,'chromebook')
    # main('https://www.newegg.com/p/pl?N=100006740%204814&Order=3&page=26','Notebook')
   
    # main(surface_laptops_url, 'surface_laptops')
    # main(surface_book_url, 'surface_book')
    # main(surface_pro_url, 'surface_pro')
    # main(surface_go_url, 'surface_go')
    # main(macbook_url, 'macbook')
    main(touch_laptops_url, 'touch_laptops')
