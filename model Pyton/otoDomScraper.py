# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 20:54:51 2021

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

from bs4 import BeautifulSoup as bs

def daneDomu(url):
    print('zbieranie danych')
    req = Request(url, headers={'User-Agent': "Mozilla/89.0"}) 
    sauce = urlopen(req).read()  # otherwise otodom.pl is safe against web scraping
    htmlPage=bs(sauce, 'html.parser')
    
    headerCena=htmlPage.find('header', class_='css-1ohj6qp eu6swcv21')
    try:
        strongCena=headerCena.find('strong', class_='css-srd1q3 eu6swcv16')
        cena=strongCena.text
    except:
        cena=0
    divContainer = htmlPage.find('div', class_='css-1d9dws4 egzohkh2')
    
    
    powierzchnia,lPokoi,powierzchniaDzialki,rokBudowy,lPieter=0,0,0,0,0
    dzielnica,rodzajZabudowy,materialBudynku,stanWykonczenia,okna,rynek='','','','','',''
    
    dzielnicaDiv=htmlPage.find_all('a', class_='css-1in5nid e1je57sb7')
    dzielnica=''
    for dz in dzielnicaDiv:
        dzielnica+=dz.text+' '
    print(dzielnica)
    try:
        divInfo=divContainer.find_all('div', class_='css-18h1kfv ev4i3ak3')
    except:
        daneDomu=[dzielnica,powierzchnia,lPokoi,powierzchniaDzialki,rodzajZabudowy,materialBudynku,rokBudowy,
              stanWykonczenia,okna,rynek,lPieter,cena]
        return daneDomu
    
    for div in divInfo:
        if div['aria-label']=='Powierzchnia działki':
            powierzchniaDzialki=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('powierzchnia działki')
        elif div['aria-label']=='Powierzchnia':
            powierzchnia=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('powierzchnia')
        elif div['aria-label']=='Rynek':
            rynek=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('rynek')
        elif div['aria-label']=='Liczba pokoi':
            lPokoi=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('LIczba pokoi')
        elif div['aria-label']=='Rodzaj zabudowy':
            rodzajZabudowy=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('Rodzaj zabudowy')
        elif div['aria-label']=='Liczba pięter':
            lPieter=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('liczba pięter')
        elif div['aria-label']=='Materiał budynku':
            materialBudynku=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('materiał budynku')
        elif div['aria-label']=='Rok budowy':
            rokBudowy=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('rok budowy')
        elif div['aria-label']=='Stan wykończenia':
            stanWykonczenia=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('stan wykonczenia')
        elif div['aria-label']=='Okna':
            okna=(div.find('div', class_='css-1ytkscc ev4i3ak0').text)
            print('okna')
            
    daneDomu=[dzielnica,powierzchnia,lPokoi,powierzchniaDzialki,rodzajZabudowy,materialBudynku,rokBudowy,
              stanWykonczenia,okna,rynek,lPieter,cena]
    return daneDomu