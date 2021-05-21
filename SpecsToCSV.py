# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 17:14:59 2021

@author: Michael Twohy
"""
import pickle
import csv
from os.path import exists

def percent_matching_keys(case, wanted_keys):
    num_matching_keys = 0
    for k in wanted_keys:
        if k in case.keys():
            num_matching_keys += 1.
    return 100 * num_matching_keys / len(wanted_keys)
       
def unwanted_brand(case, unwanted_brands):
    return ('Brand' in case.keys() and contains(case['Brand'], unwanted_brands))
    
def filter_cases(dict_list, keys, unwanted_brands, case_fullness_threshold = 100):
    filtered = list()
    for d in dict_list:
        dict_copy = dict()
        if percent_matching_keys(d,keys) >= case_fullness_threshold \
        and not unwanted_brand(d,unwanted_brands):
            for k in keys:
                if k in d.keys():
                    dict_copy[k] = d[k]
            filtered.append(dict_copy)
    return filtered

def create_csv_filename(filename):
    filename = filename+"%s"+'.csv'
    i = 0
    while exists(filename % i):
        i += 1
    return filename % i

def save_as_csv(cases, keys, filename = 'newEgg_Scrape'):
    filename = create_csv_filename(filename)
    with open(filename, 'w', newline = '') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()
        dict_writer.writerows(cases)
    print('Created', filename,'with',len(cases),'cases')
    
def load_pickle(filename):
    with open(filename+'.pickle', 'rb') as file:
        p = pickle.load(file)
    return p

def combine_pickles(pickles):
    specs = list()
    for p in pickles:
        for case in load_pickle(p):
            case['Class'] = p
            specs.append(case)
        # specs.extend(spec)
    return specs


#in s, find the 
# def get_clockSpeed(s, unit, start_offset, end_offset=1):
#      buffer = ''
#      for i in range(len(s)):
#          if s[i] == unit[len(buffer)]:
#              buffer = buffer + s[i] #build buffer
#              if buffer == unit:
#                  start = i-(len(unit)-1) - start_offset
#                  end = i-(len(unit)-1) - end_offset
#                  return s[start : end]
#          else:
#              buffer = '' #reset buffer
        
def get_spec_from_string(s, unit):
    s = s.replace('(','')
    s = s.replace(')','')
    s = s.replace(',','')
    s = s.split()
    # print("length:",len(s))
    for i in range(len(s)):
        # print(i,":",s[i])
        
        if s[i] == unit:
            return s[i-1]
    return ''




def get_storage_type(s):
    if 'TB' in s:
        return 'TB'
    return 'GB'

def contains(s,keywords):
    for word in keywords:
        if word.upper() in s.upper():
            return True
    return False

def matches(s,keywords):
    ret = list()
    slist = s.upper().split()
    for word in slist:
        if word.upper() in keywords:
           ret.append(word.upper())
    return ret    

def get_storage(s):
    s = s.replace('(',' ').replace(')',' ').replace(',',' ')
    units = matches(s,('GB,TB'))
    s = s.split()    
    drives = list()
    
    i=0 #keeps track of what word we're looking at 
    u=0 #keeps track of what unit we're looking for 
    while i<len(s) and u<len(units):
        if s[i] == units[u]:
            storage = float(s[i-1])
            if units[u] == 'TB':
                storage*=1000
            drives.append(storage)
            u+=1
        i+=1
    return drives

#DISCLAIMER: This method is disgusting, but it works. 
def filter_variables(cases):
    # eliminate invalid Touchscreen values
    for c in cases:
        if 'Touchscreen' in c.keys():
            if c['Touchscreen'] != 'Yes' and c['Touchscreen'] != 'No':
                c['Touchscreen'] = 'Yes'
    
    for c in cases:
        if 'Touchscreen' in c.keys():
             if c['Touchscreen'] == 'Yes':
                c['Touchscreen'] = 1     
             elif c['Touchscreen'] == 'No':
                c['Touchscreen'] = 0  
 
    # eliminate invalid Graphics Type values
    for c in cases:
        if 'Graphic Type' in c.keys():
            if contains(c['Graphic Type'], ('Dedicated','NVIDIA','AMD','GeForce','Quadro','Radeon')):
                 c['Graphic Type'] = 'Dedicated'
            elif contains(c['Graphic Type'], ('Integrated','Intel')):
               c['Graphic Type'] = 'Integrated'
        else:
            if 'Graphics Card' in c.keys():
                if contains(c['Graphics Card'],('NVIDIA' 'AMD')):
                    c['Graphic Type'] = 'Dedicated'
                else: 
                    c['Graphic Type'] = ''
        
    for c in cases:
        if 'Operating System' in c.keys():
            if 'Windows' in c['Operating System']:
                c['Operating System'] = 'Windows'
            elif 'Chrome OS' in c['Operating System']:
                c['Operating System'] = 'Chrome OS'
            elif contains(c['Operating System'],('Mac OS','iOS')):
                c['Operating System'] = 'Mac OS'    
            else:
                c['Operating System'] = ''    


    
    #split memory
    for c in cases:
        if 'Memory' in c.keys():
            c['Memory'] = get_spec_from_string(s = c['Memory'], unit = 'GB')
    
    #split CPU speed
    for c in cases:
        if 'CPU Speed' in c.keys():
            c['CPU Speed'] = get_spec_from_string(s = c['CPU Speed'], unit = 'GHz')
    
    for c in cases:
        if 'Screen Size' in c.keys():
            c['Screen Size'] = c['Screen Size'].replace('"', '').split()[0]
            
    
    #if case doesn't have storage, but it does have SSD, add SSD value to 
    #Storage and set SSD to 1
    for c in cases:
        if 'Storage' not in c.keys() and 'SSD' in c.keys():
            c['Storage'] = c['SSD']
            c['SSD'] = 1
    
    for c in cases:
        if 'Storage' in c.keys():
            if '+' in c['Storage'] or 'SSD' in c['Storage']:
                c['SSD'] = 1
            else: 
                c['SSD'] = 0
    
    for c in cases:
        if 'Battery' in c.keys():
            s = c['Battery'].lower()
            s = s.replace('whrs',' wh')
            s = s.replace('whr',' wh')
            s = s.replace('whs',' wh') 
            s = s.replace('wh',' wh')
            

            if 'wh' in s:
                c['Battery'] = get_spec_from_string(s, unit = 'wh')
            else:
                c['Battery'] = ''
    
    for c in cases:
        if 'Graphics Card' in c.keys():
            if contains(c['Graphics Card'],('nvidia','geforce','quadro')):
                c['GPU Brand'] = 'NVIDIA'
            elif contains(c['Graphics Card'],('amd','radeon')): 
                c['GPU Brand'] = 'AMD'
            else: 
                c['Graphic Type'] = ''
    
        if 'CPU' in c.keys():
            if contains(c['CPU'],('Intel','i3','i5','i7','i9')):
                c['CPU Brand'] = 'Intel'
            elif contains(c['CPU'],('amd','Ryzen')):
                c['CPU Brand'] = 'AMD'
            else: 
                c['CPU Brand'] = ''    

    for c in cases:
        if 'Storage' in c.keys():
            storage = sum(get_storage(c['Storage']))
            if storage > 0:
                c['Storage'] = str(storage)
            else:
                c['Storage'] = ''
      
    for c in cases:
        if 'Rating' in c.keys():
            if c['Rating'] == "NA":
                c['Rating'] = None
  
    for c in cases:
        if 'Brand' in c.keys():
            c['Brand'] = c['Brand'].lower()
        
    for c in cases: 
        if 'Class' in c.keys():
            pickle_name = c['Class']
            if 'gaming' in pickle_name:
                 c['Class'] = 'Gaming'
            elif 'Notebook' in pickle_name:
                c['Class'] =  'NoteBook'
            elif 'mobileWorkstation' in pickle_name:
                c['Class'] =  'MobileWorkstation'      
            elif 'chromebook' in pickle_name:
                c['Class'] =  'ChromeBook'       
            elif '2in1' in pickle_name or 'surface' in pickle_name:
                c['Class'] =  '2in1'
            elif 'macbook' in pickle_name:
                c['Class'] =  'MacBook'


def to_binary(cases, variable, value1, value0):
    for c in cases: 
        if variable in c.keys():
            if c[variable] == value1:
                c[variable] = 1
            elif c[variable] == value0:
                c[variable] = 0
    
def cases_to_binary(cases):
    to_binary(cases, 'CPU Brand', 'Intel', 'AMD')
    to_binary(cases, 'GPU Brand', 'NVIDIA', 'AMD')
    to_binary(cases, 'Graphic Type', 'Dedicated', 'Integrated')


    
def main():
    pickles = ['PickledSpecs_gaming0',
               'PickledSpecs_Notebook',
               'PickledSpecs_Notebook_p26-100',
               'PickledSpecs_mobileWorkstation0',
               'PickledSpecs_chromebook0',
               'PickledSpecs_2in1_0','PickledSpecs_macbook0',
               'PickledSpecs_surface_book0',
               'PickledSpecs_surface_go0',
               'PickledSpecs_surface_pro0',
               'PickledSpecs_surface_laptops0']
    
    wanted_keys = ['Brand', 
                   'Model', 
                   'Operating System', 
                   'Price',
                   'Rating',
                   'CPU Brand',
                   'CPU',
                   'CPU Speed',
                   'GPU Brand',
                   'Graphics Card',
                   'Graphic Type',
                   'Memory',
                   'Storage', 
                   'Screen Size', 
                   'Touchscreen',
                   'Battery',
                   'SSD',
                   'Class'
                   ]

    
    unwanted_brands = ['XOTIC PC', 'KUU', 'Vicabo', 'Jumper', 'Eluktronics',
                       'A&D Electronics','Abit','CENAVA','CORN','ETopSell',
                       'EVOO','EVOC','Gateway','HAOQIN','Hasee','HD Camera',
                       'Hyundai','iView','LHMZNIY','Lsxvern','NEXGEN',
                       'One-NetBook','SUPERSONIC','Thunderobot','VOYO','XPG']
    
    cases = filter_cases(combine_pickles(pickles), wanted_keys, unwanted_brands, 70)
    filter_variables(cases)
    cases_to_binary(cases)
    save_as_csv(cases, wanted_keys, filename = 'Test_CSV')    
    
if __name__ == "__main__":
    main()
    
