# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 20:14:34 2021

@author: Lenovo
"""
import re
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen
from urllib.request import urlretrieve
import argparse
import json
import math
import os
import time
from urllib.error import HTTPError
from urllib.parse import ParseResult
import pandas as pd
from otoDomScraper import daneDomu
from random import randrange
from bs4 import BeautifulSoup as bs
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns

def daneStrony(url):
    req = Request(url, headers={'User-Agent': "Chrome/91.0"}) 
    sauce = urlopen(req).read()  # otherwise otodom.pl is safe against web scraping
    htmlPage=bs(sauce, 'html.parser')
    return htmlPage

def linksDownload():
    links=[]
    for i in range(1,89):
        print(i)
        #url='https://www.otodom.pl/pl/oferty/sprzedaz/dom/wiele-lokalizacji?distanceRadius=0&market=ALL&page='+str(i)+'&limit=24&by=DEFAULT&direction=DESC&locations%5B0%5D%5BregionId%5D=7&locations%5B0%5D%5BcityId%5D=920&locations%5B0%5D%5BsubregionId%5D=198&locations%5B1%5D%5BregionId%5D=7&locations%5B1%5D%5BcityId%5D=37519&locations%5B1%5D%5BsubregionId%5D=198&locations%5B2%5D%5BregionId%5D=7&locations%5B2%5D%5BcityId%5D=920&locations%5B2%5D%5BdistrictId%5D=1993&locations%5B2%5D%5BsubregionId%5D=198'
        url='https://www.otodom.pl/pl/oferty/sprzedaz/dom/warszawa?distanceRadius=0&market=ALL&page='+str(i)+'&limit=24&by=DEFAULT&direction=DESC&locations[0][regionId]=7&locations[0][cityId]=26&locations[0][subregionId]=197'
        Page=daneStrony(url)
        ls=Page.find_all('a', class_='css-19ukcmm es62z2j25')
        for l in ls:
            links.append(l['href'])
        time.sleep(2) 
    
    links=list(set(links))
    
    path='C:\\Users\\Lenovo\\Desktop\\otodom-scrapper-master\\src\\'
    file='urls_warszawa.txt'
    
    f=open(path+file,'w')
    for ele in links:
        f.write('https://www.otodom.pl'+ele+'\n')
    f.close()
    return links

def toNum2(txt):
    if type(txt) is int:
        return txt
    elif (type(txt) is str):
        digs=re.findall(r'\d+', txt)
        if len(digs)==1:
            return int(digs[0])
        elif len(digs)==2:
            return 1000*int(digs[0])+int(digs[1])
        elif len(digs)==3:
            return 1000000*int(digs[0])+1000*int(digs[1])+int(digs[0])
        
     #   return int(digs)

    
def toNum1(txt):
    if type(txt) is str:
        digs=re.findall(r'\d+', txt)
        if len(digs)==1:
            return int(digs[0])
        elif len(digs)==2 and (txt[1]!=' '):
            return int(digs[0])+0.01*int(digs[1])
        elif len(digs)==3:
            return 1000*int(digs[0])+int(digs[1])+0.001*int(digs[2])
        elif (type(txt) is str) and (txt[1]==' '): 
            digs=re.findall(r'\d+', txt)
            return 1000*int(digs[0])+int(digs[1])
    else:
        return txt
    
def toNum3(txt):
    if type(txt)==int:
        return txt
    return int(re.findall(r'\d+', txt)[0])
    
def dzielnice(txt):
    if 'Dąbrowa' in txt:
        return 'Dąbrowa'
    elif 'Dolne' in txt:
        return 'Dolne'
    else:
        return 'Łomianki'
    
def dzielniceWaw(txt):
    
    if type(txt) is float:
        return ''
    elif len(txt.split())>5 and 'Łomianki' not in txt:
        waw=txt.split()
        return waw[5]
    elif 'Łomianki' in txt:
        if 'Dąbrowa' in txt:
            return 'Dąbrowa'
        elif 'Dolne' in txt:
            return 'Dolne'
        else:
            return 'Łomianki'
    else:
        return txt
    
def pietra(txt):
     if type(txt) is str:
         if '1' in txt:
             return 1
         elif '2' in txt:
             return 2
         elif '3' in txt:
             return 3
         elif 'parterowy' in txt:
             return 0
     else:
            return txt
         

linksWarszawa=linksDownload()

urls=[]
path='C:\\Users\\Lenovo\\Desktop\\otodom-scrapper-master\\src\\'
file='urls_lomianki.txt'
with open(path+file) as f:
    urls=f.readlines()


listaLomianki=[]
i=0
for link in urls:
    #if i<4259:
    #    i=i+1
    #    continue
    print(i)
    print(link)
    try:
        dane=daneDomu(link)
    except:
        print('porazka')
    listaLomianki.append(dane)
    i=i+1
    time.sleep(randrange(2)) 

dfLomianki=pd.DataFrame(listaLomianki,columns=['dzielnica','powierzchnia','lPokoi','powierzchniaDzialki','rodzajZabudowy','materialBudynku','rokBudowy',
              'stanWykonczenia','okna','rynek','lPieter','cena'])
dfWarszawa.to_csv('dfWarszawa')
dfWarszawa1=pd.read_csv('dfWarszawa',index_col=0)

concat=pd.concat([dfLomianki, dfWarszawa1], join="inner")

concat['powierzchnia_corr']=concat['powierzchnia'].apply(lambda x: toNum1(x))
concat['powierzchniaDzialki_corr']=concat['powierzchniaDzialki'].apply(lambda x: toNum2(x))
concat['cena_corr']=concat['cena'].apply(lambda x: toNum2(x))

concat['rokBudowy_corr']=concat['rokBudowy'].apply(lambda x: toNum3(x))

concat['cena/m']=concat['cena_corr']/concat['powierzchnia_corr']
concat['dzielnica_corr']=concat['dzielnica'].apply(lambda x:dzielniceWaw(x))
concat['lPieter_crr']=concat['lPieter'].apply(lambda x: pietra(x))
     
concat=concat[concat['powierzchnia_corr']>0]
concat=concat[concat['cena_corr']>0]
concat['lPokoi']=concat['lPokoi'].apply(lambda x: toNum3(x))

concat=pd.get_dummies(concat,columns=['rodzajZabudowy','materialBudynku','stanWykonczenia','okna','rynek','dzielnica_corr'])
concat=concat.drop(['dzielnica','powierzchnia','powierzchniaDzialki','lPieter','cena','cena_corr'],axis=1)

concat['rokBudowy']=concat['rokBudowy'].replace(to_replace=0,value=1990)

concat['rokBudowy']=concat['rokBudowy'].astype('int')
concat=concat.fillna(0)
concat['cena/m'].hist()
concat=concat[concat['cena/m']<2e6]
concat['cena/m'].hist(bins=200)
concat=concat[concat['cena/m']<40000]
concat['cena/m'].hist(bins=200)
y=concat.loc[:,'cena/m'].values
x=concat.drop(['cena/m'],axis=1).iloc[:,:].values

rf=RandomForestRegressor(max_depth=30,max_features=10,min_samples_leaf=3,min_samples_split=2)
rf=RandomForestRegressor()
rf.fit(x,y)
rf.score(x,y)
import pickle

pickle.dump(rf, open('rf_model', 'wb'))
from sklearn.model_selection import GridSearchCV
param_grid = {
    'bootstrap': [True],
    'max_depth': [2,3,5,10,20,30,50],
    'max_features': [2, 3,5,10],
    'min_samples_leaf': [3, 4, 5],
    'min_samples_split': [2,3,5,10,20,30],
}

grid_search = GridSearchCV(estimator = rf, param_grid = param_grid, 
                          cv = 3, n_jobs = -1, verbose = 2)

grid_search.fit(x,y)
grid_search.best_params_

import statistics

roznica_wzg=abs(y-rf.predict(x))/y
std=statistics.stdev(roznica_wzg)
concat_stat=concat.copy()
concat_stat['std_rel']=roznica_wzg
#clustering 
from sklearn.cluster import AffinityPropagation
clustering = AffinityPropagation(random_state=5).fit(concat_stat.iloc[:,:].values)
concat_stat['clusters']=clustering.labels_


from sklearn.model_selection import cross_val_score, cross_val_predict
cv_r2_scores_rf = cross_val_score(rf, x, y, cv=2,scoring='r2')
print(cv_r2_scores_rf)
print("Mean 5-Fold R Squared: {}".format(np.mean(cv_r2_scores_rf)))


importance=rf.feature_importances_
columns=concat.drop(['cena/m'],axis=1).columns.values
df_importance=pd.DataFrame(importance,columns)


plt.figure(figsize=(15,15))
plt.scatter(df_importance[0],df_importance.index)
plt.show()


dfWarszawa['dzielnica'].unique()[6]
g = sns.histplot(data=concat, x='cena/m',hue='lPokoi', multiple="stack")
g = sns.histplot(data=concat, x='cena/m',hue='rokBudowy_corr', multiple="stack")

Łomianki_wtorny_nasz=dfWarszawa[(dfWarszawa['dzielnica_corr']=='Łomianki') & (dfWarszawa['rynek']=='wtórny') &
                           (dfWarszawa['stanWykonczenia']=='do zamieszkania')]
g = sns.histplot(data=Łomianki_wtorny, x='cena/m',hue='stanWykonczenia', multiple="stack")
g.set(xlim=(1000, 10000))

plt.scatter(Łomianki_wtorny_nasz['rokBudowy_corr'],Łomianki_wtorny_nasz['cena/m'])
plt.xlim(1990,2022)

plt.scatter(Łomianki_wtorny_nasz['powierzchniaDzialki_corr'],Łomianki_wtorny_nasz['cena/m'])
plt.xlim(0,3000)

plt.scatter(Łomianki_wtorny_nasz['powierzchniaDzialki_corr']*Łomianki_wtorny_nasz['rokBudowy_corr']
            ,Łomianki_wtorny_nasz['cena/m'])
plt.xlim(0,0.4E7)

g = sns.histplot(data=Łomianki_wtorny_nasz, x='cena/m',hue='lPokoi', multiple="stack")
g.set(xlim=(1000, 10000))

g = sns.histplot(data=Łomianki_wtorny_nasz, x='cena/m',hue='rodzajZabudowy', multiple="stack")
g.set(xlim=(1000, 10000))


x1=np.array([4,2003,130,100,2003,1,#6 wstepne
            0,0,0,0,1,0, #6 szeregowiec
            0,0,0,0,0,0,0,1,0, #9 beton
            0,0,0,1,0,0,#6 do zamieszkania
            0,0,0,1,#okna plastikowe
            0,1,#rynek wtorny
            0,0,0,0,0,0,0,0,0,0,#dzielnica Praga-Poł
            0,0,0,0,0,0,0,0,0,0,#dzielnica cd
            1,0,0,#łomianki
            ])
x1=np.transpose(x1.reshape(-1,1))
rf.predict(x1)#7260 zł/m

x2=np.array([6,2021,180,1000,2002,1,
            0,0,0,0,0,1, #szeregowiec
            0,0,1,0,0,0,0,0,0, #beton
            0,0,1,0,0,0,#do zamieszkania
            0,0,0,1,#okna plastikowe
            0,1,#rynek wtorny
            0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,#ródmiecie
            ])

x2=np.transpose(x2.reshape(-1,1))
rf.predict(x2)

x3=np.array([5,2003,112,1,2003,1,
            0,0,0,0,1,0, #szeregowiec
            0,0,0,1,0,0,0,0,0, #beton
            0,0,0,1,0,0,#do zamieszkania
            0,0,0,1,#okna plastikowe
            0,1,#rynek wtorny
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,#łomianki
            ])
x3=np.transpose(x3.reshape(-1,1))
rf.predict(x3)#7260 zł/m
6434*