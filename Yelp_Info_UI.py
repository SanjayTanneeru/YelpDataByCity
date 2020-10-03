# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29, 2020
About - It fetches all restaurant data based on city search from Yelp.
--It uses simple user interface created using Tkinter library
--This project was created for learning purpose
@author: Sanjay Tanneeru
"""

#Import Libraries
import pandas as pd,re,urllib.request,time,sys,random
from bs4 import BeautifulSoup
from datetime import datetime
import tkinter as tk, os
from tkinter import filedialog,messagebox

#Fetches the data entered by user on the simple UI form
def fetch(entries):
    global cityvar
    for entry in entries:
        text  = entry[1].get()
        cityvar = text
        return
    
def makeform(root, fields):
    entries = []
    for field in fields:
        #Creating frame and setting position
        row = tk.Frame(root)
        row.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        
        #Create lables, entry and buttons
        lab = tk.Label(row, width=15, text=field, anchor='w')
        ent = tk.Entry(row)

        #Pack all together
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        
        entries.append((field, ent))
    return entries

def selectFolder():
    global pathvar
    SelectedFolder = filedialog.askdirectory(parent=root,
                                 initialdir=os.getcwd(),
                                 title="Please select a folder:")
    if SelectedFolder == '':
        return
    else:
        res = messagebox.askyesnocancel("Selected Directory",SelectedFolder)
        if res == True:
            messagebox.showinfo("Directory set to -",SelectedFolder)
            pathvar = SelectedFolder
            return
        elif res == False:
            #Retry
            selectFolder()
        else:
            return

def Run(entries):
    #Enter Input
    #Use Tkinter and get user input and where to save
    
    global cityvar
    global pathvar
    
    if pathvar == '':
        messagebox.showerror(title = 'Error', message='No Folder found, please select a folder')
        return
    else:
        pass
    
    for entry in entries:
        text  = entry[1].get()
        cityvar = text
    
    FinalcityVar     = cityvar   #Get city name from yelp
    FinalFilename    = pathvar   #Name of the csv file
    
    print('Running Yelp for City:', FinalcityVar)
    
    #Formatting space with '+' and ',' with '%2C' cause thats how Yelp accepts
    FinalcityVar = FinalcityVar.replace(' ','+').replace(',','%2C')
    
    
    #Fetch no. of pages to iterate through
    header      = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}    
    BaseUrl     = 'https://www.yelp.com/search?find_desc=&find_loc={}&ns=1&start='.format(FinalcityVar)
    BaseReq     = urllib.request.Request(BaseUrl, headers = header)    
    Basehtml    = urllib.request.urlopen(BaseReq) 
    pagesSoup   = BeautifulSoup(Basehtml,'html.parser')    
    pages       = pagesSoup.find('div',class_='lemon--div__09f24__1mboc border-color--default__09f24__R1nRO text-align--center__09f24__31irQ').text    
    finalPages  = pages[-2:]
    
    #Use no. of pages to iterate and get href for each restaurant to scrape information from 
    #Get initial set of restaurant links
    InitialLinks = []
    for p in range(0, int(finalPages)*10, 10):
        time.sleep(random.randint(1,2))
        print(p) 
        
        BaseReq     = urllib.request.Request(BaseUrl+str(p), headers = header)
        links       = urllib.request.urlopen(BaseReq)
        linksSoup   = BeautifulSoup(links,'html.parser')
        AllLinks    = linksSoup.findAll('a')
    
        #Get href for each restaurant to scrape information from 
        for i in AllLinks:
            if re.search('biz',str(i)):
                if re.search('hrid',str(i)):
                    continue
                elif 'http://www.yelp.com' + i['href'] not in InitialLinks:    
                    InitialLinks.append('http://www.yelp.com' + i['href'])
    
    #Define lists  
    RestaurantLink,RestName,Rating,Reviews,Expensive,Cuisine,Website,Phone,Address,Updatedservices,HealthSafetyMeasures = ([] for i in range(11))
    
    #Process each link to get information
    cnt = 0
    for L in InitialLinks:
        cnt+=1
        time.sleep(random.randint(1,2))
        print('processing ', cnt, 'of', len(InitialLinks))
        
        BaseReq  = urllib.request.Request(L, headers = header)
        try:
            link = urllib.request.urlopen(BaseReq)
        except:
            print('skipping')
        
        PreData = BeautifulSoup(link,'html.parser')
        Data  = PreData.find('div',class_='main-content-wrap main-content-wrap--full')
        
        #Restaurant Link
        RestaurantLink.append(L)
        
        #Restaurant Name
        try:
            RestName.append(Data.find('h1').text)
        except:
            RestName.append('')
        
        #Restaurant Rating
        try:
            RatingTag = Data.find('div',class_='lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT border-color--default__373c0__3-ifU').find('div')
            Rating.append(RatingTag.get('aria-label'))
        except:
            Rating.append('')
        
        #Reviews
        try:
            tmpReviews = Data.find('p',class_='lemon--p__373c0__3Qnnj text__373c0__2Kxyz text-color--mid__373c0__jCeOG text-align--left__373c0__2XGa- text-size--large__373c0__3t60B').text
            Reviews.append(tmpReviews)
        except:
            Reviews.append('')
        
        #Expensive
        try:
            exp_FinalVal = Data.findAll('span',class_='lemon--span__373c0__3997G display--inline__373c0__3JqBP margin-r1__373c0__zyKmV border-color--default__373c0__3-ifU')[0].text
            Expensive.append(exp_FinalVal.strip())
        except:
            Expensive.append('')
            
        
        #Cuisine
        try:
            CuisineTemp = Data.findAll('span',class_='lemon--span__373c0__3997G display--inline__373c0__3JqBP margin-r1__373c0__zyKmV border-color--default__373c0__3-ifU')[1].text
            Cuisine.append(CuisineTemp)
        except:
            Cuisine.append('')
        
        #Website and phone details
        tempWebsite = ''
        tempPhone = ''
        TempWebsitephone = ''
        
        try:
            TempWebsitephone = Data.find('div',class_='lemon--div__373c0__1mboc padding-t3__373c0__1gw9E padding-r3__373c0__57InZ padding-b3__373c0__342DA padding-l3__373c0__1scQ0 border--top__373c0__3gXLy border--right__373c0__1n3Iv border--bottom__373c0__3qNtD border--left__373c0__d1B7K border-radius--regular__373c0__3KbYS background-color--white__373c0__2uyKj').findAll('div')
        except:
            TempWebsitephone = ''

        #Get Website
        for h in TempWebsitephone:        
            if re.search('Business website',str(h)):
                try:
                    tmpwebsite = re.search(r'Business[^*]+',h.text).group()
                except:
                    tmpwebsite = ''
                tempWebsite = tmpwebsite.replace('Business website','')
                Website.append(tempWebsite.strip())
                break
        
        if tempWebsite == '':
            Website.append('')
            
        #Get Phone number
        for k in TempWebsitephone:
            if re.search('Phone number',str(k)):
                try:
                    tmpphoneno = re.search(r'Phone[^*]+',k.text).group()
                except:
                    tmpphoneno = ''
                
                tempPhone = tmpphoneno.replace('Phone number','')
                Phone.append(tempPhone.strip())
                break
            
        if tempPhone == '':    
            Phone.append('')
                
        #Address
        try:
            Address.append(Data.find('address', class_='lemon--address__373c0__2sPac').text)
        except:
            Address.append('')
        
        #Processing Updated services and health& safety measures
        #Get the section tag to capture updated services and health& safety measures
        preSection = ''
        try:
            temp1 = Data.find('section')
    
            for var in temp1.findAll('div'):
                if re.search('Updated Services',var.text):
                    preSection = var.findAll('span')
                    break
        except:
            preSection = ''
            pass


        preSection = [i.text for i in preSection]
        
        #Get UpdatesServices index and Health & Safety Measures index
        try:
            U_S = preSection.index('Updated Services')
            
            H_SM = preSection.index('Health & Safety Measures')
            
            #Updatedservices
            tmp_updatedServices = ''
            for m in range(U_S,H_SM-1):
                if preSection[m] == '':
                    pass
                else:
                    tmp_updatedServices += ','+preSection[m]
            
            tmp_updatedServices = tmp_updatedServices.replace(',Updated Services','')[1:]
            try:
                Updatedservices.append(tmp_updatedServices)
            except:
                Updatedservices.append('')
                
                    
            #Health&SafetyMeasures
            tmp_healthsafetyservices = ''
            for n in range(H_SM,len(preSection)):
                if preSection[n] == '':
                    pass
                else:
                    tmp_healthsafetyservices += ','+preSection[n]
            
            tmp_healthsafetyservices = tmp_healthsafetyservices.replace(',Health & Safety Measures','')[1:]
            try:
                HealthSafetyMeasures.append(tmp_healthsafetyservices)
            except:
                HealthSafetyMeasures.append('')
        except:
            Updatedservices.append('')
            HealthSafetyMeasures.append('')
    
    #Create dataframe
    outputForYelp = pd.DataFrame(columns = ['RestLink','Name','Rating','Reviews','Expensive','Cuisine','WebsiteInfo','PhoneNumber','Address','Updatedservices','HealthSafetyMeasures'])

    outputForYelp['RestLink']               = RestaurantLink
    outputForYelp['Name']                   = RestName
    outputForYelp['Rating']                 = Rating
    outputForYelp['Reviews']                = Reviews
    outputForYelp['Expensive']              = Expensive
    outputForYelp['Cuisine']                = Cuisine
    outputForYelp['WebsiteInfo']            = Website
    outputForYelp['PhoneNumber']            = Phone
    outputForYelp['Address']                = Address
    outputForYelp['Updatedservices']        = Updatedservices
    outputForYelp['HealthSafetyMeasures']   = HealthSafetyMeasures
    
    #Modify file name based on user input
    FinalcityVar = FinalcityVar.replace(',','').replace(' ','_') + '_' + datetime.now().strftime('%m%d%Y_%H%M')
    
    outputForYelp.to_csv(FinalFilename + '/' + FinalcityVar + '.csv')
    
    sys.exit()
    
if __name__ == '__main__':
    
    fields = ['Enter City:']
    
    global cityvar 
    global pathvar
    global ents
    
    cityvar = ''
    pathvar = ''
    
    root = tk.Tk()
    ents = makeform(root, fields)
    root.bind('<Return>', (lambda event, e=ents: fetch(e)))   

    b1 = tk.Button(root, text='Folder',command=(lambda e=ents: selectFolder()))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    
    b2 = tk.Button(root, text='Run',command=(lambda e=ents: Run(e)))
    b2.pack(side=tk.LEFT, padx=5, pady=5)
    
    root.mainloop()
    
    
    