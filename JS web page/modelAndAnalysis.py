import pandas as pd
#from otoDomScraper import daneDomu
#from random import randrange
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns
import re
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split


def toNum2(txt):
    if type(txt) is int:
        return txt
    elif (type(txt) is str):
        digs = re.findall(r'\d+', txt)
        if len(digs) == 1:
            return int(digs[0])
        elif len(digs) == 2:
            return 1000 * int(digs[0]) + int(digs[1])
        elif len(digs) == 3:
            return 1000000 * int(digs[0]) + 1000 * int(digs[1]) + int(digs[0])

    #   return int(digs)


def toNum1(txt):
    if type(txt) is str:
        digs = re.findall(r'\d+', txt)
        if len(digs) == 1:
            return int(digs[0])
        elif len(digs) == 2 and (txt[1] != ' '):
            return int(digs[0]) + 0.01 * int(digs[1])
        elif len(digs) == 3:
            return 1000 * int(digs[0]) + int(digs[1]) + 0.001 * int(digs[2])
        elif (type(txt) is str) and (txt[1] == ' '):
            digs = re.findall(r'\d+', txt)
            return 1000 * int(digs[0]) + int(digs[1])
    else:
        return txt


def toNum3(txt):
    if type(txt) == int:
        return txt
    return int(re.findall(r'\d+', txt)[0])

'''
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
    elif len(txt.split()) > 5 and 'Łomianki' not in txt:
        waw = txt.split()
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
'''

def pietra(txt):
    if type(txt) is str:
        if '0' in txt:
            return 0
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

def cities(x):
    dist=x.split()[4]
    #city=x.split()[5]
    if dist=='warszawski':
        return x.split()[6]
    elif dist in ['Warszawa','Radom','Płock','Siedlce']:
        return dist
    else:
        try:
            return x.split()[5]
        except:
            return 'unknown'

def region(x):
    if x.split()[4]=='Warszawa':
        try:
            return x.split()[5]
        except:
            return ''
    else:
        return ''

dfMazowieckie=pd.read_csv('dfMazowieckie.csv',index_col=0)
concat=dfMazowieckie

#dfWarszawa1 = pd.read_csv('dfWarszawa', index_col=0)

#concat = pd.concat([dfLomianki, dfWarszawa1], join="inner")

concat['powierzchnia_corr'] = concat['powierzchnia'].apply(lambda x: toNum1(x))
concat['powierzchniaDzialki_corr'] = concat['powierzchniaDzialki'].apply(lambda x: toNum2(x))
concat['cena_corr'] = concat['cena'].apply(lambda x: toNum2(x))

concat['rokBudowy_corr'] = concat['rokBudowy'].apply(lambda x: toNum3(x))

concat['cena/m'] = concat['cena_corr'] / concat['powierzchnia_corr']
#concat['dzielnica_corr'] = concat['dzielnica'].apply(lambda x: dzielniceWaw(x))
concat['lPieter_crr'] = concat['lPieter'].apply(lambda x: pietra(x))

concat = concat[concat['powierzchnia_corr'] > 0]
concat = concat[concat['cena_corr'] > 0]
concat['lPokoi'] = concat['lPokoi'].apply(lambda x: toNum3(x))
#ustalanie powiatów
concat['districts']=concat['dzielnica'].apply(lambda x: x.split()[4])
cities_corr=concat['dzielnica'].apply(lambda x: cities(x))
concat['cities_corr']=cities_corr
region=concat['dzielnica'].apply(lambda x: region(x))
concat['region_corr']=region
cities_counts=cities.value_counts(ascending=False)

###to poniżej powinno być ostatnią linijką poprawy
concat = pd.get_dummies(concat, columns=['rodzajZabudowy', 'materialBudynku', 'stanWykonczenia', 'okna', 'rynek',
                                         'cities_corr','districts','region_corr'])
############
concat_dropped = concat.drop(['dzielnica', 'powierzchnia', 'powierzchniaDzialki', 'lPieter', 'cena', 'cena_corr',], axis=1)

concat_dropped['rokBudowy'] = concat_dropped['rokBudowy'].replace(to_replace=0, value=1990)

concat_dropped['rokBudowy'] = concat_dropped['rokBudowy'].astype('int')
concat_dropped = concat_dropped.fillna(0)
concat_dropped['cena/m'].hist()
concat_dropped = concat_dropped[concat_dropped['cena/m'] < 2e6]
concat_dropped['cena/m'].hist(bins=200)
plt.hist(concat_dropped['cena/m'],bins=200)

concat_dropped = concat_dropped[concat_dropped['cena/m'] < 100000]
plt.hist(concat_dropped['cena/m'],bins=200)

concat_dropped = concat_dropped[concat_dropped['cena/m'] < 20000]
concat_dropped['cena/m'].hist(bins=200)

y = concat_dropped.loc[:, 'cena/m'].values
x = concat_dropped.drop(['cena/m'], axis=1).iloc[:, :].values

rf = RandomForestRegressor()
param_grid = {
    'bootstrap': [True],
    'max_depth': [2, 3, 5, 10, 20, 30, 50],
    'max_features': [20,30,50],
    'min_samples_leaf': [3, 4, 5],
    'min_samples_split': [2, 3, 5, 10, 20, 30],
}

grid_search = GridSearchCV(estimator=rf, param_grid=param_grid,
                           cv=3, n_jobs=-1, verbose=1)
grid_search.fit(x, y)
grid_search.best_params_

rf = RandomForestRegressor(max_depth=50, max_features=50, min_samples_leaf=3, min_samples_split=2)

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
rf.fit(X_train, y_train)
rf.score(X_train, y_train)
rf.score(X_test, y_test)
import pickle

pickle.dump(rf, open('rf_model', 'wb'))






import statistics

roznica_wzg = abs(y - rf.predict(x)) / y
std = statistics.stdev(roznica_wzg)
concat_stat = concat.copy()
concat_stat['std_rel'] = roznica_wzg
# clustering
from sklearn.cluster import AffinityPropagation

clustering = AffinityPropagation(random_state=5).fit(concat_stat.iloc[:, :].values)
concat_stat['clusters'] = clustering.labels_

from sklearn.model_selection import cross_val_score, cross_val_predict

cv_r2_scores_rf = cross_val_score(rf, x, y, cv=2, scoring='r2')
print(cv_r2_scores_rf)
print("Mean 5-Fold R Squared: {}".format(np.mean(cv_r2_scores_rf)))

importance = rf.feature_importances_
columns = concat.drop(['cena/m'], axis=1).columns.values
df_importance = pd.DataFrame(importance, columns)

plt.figure(figsize=(15, 15))
plt.scatter(df_importance[0], df_importance.index)
plt.show()

x1 = np.array([4, 2003, 130, 100, 2003, 1,  # 6 wstepne
               0, 0, 0, 0, 1, 0,  # 6 szeregowiec
               0, 0, 0, 0, 0, 0, 0, 1, 0,  # 9 beton
               0, 0, 0, 1, 0, 0,  # 6 do zamieszkania
               0, 0, 0, 1,  # okna plastikowe
               0, 1,  # rynek wtorny
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # dzielnica Praga-Poł
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # dzielnica cd
               1, 0, 0,  # łomianki
               ])
x1 = np.transpose(x1.reshape(-1, 1))
rf.predict(x1)  # 7260 zł/m

x2 = np.array([6, 2021, 180, 1000, 2002, 1,
               0, 0, 0, 0, 0, 1,  # szeregowiec
               0, 0, 1, 0, 0, 0, 0, 0, 0,  # beton
               0, 0, 1, 0, 0, 0,  # do zamieszkania
               0, 0, 0, 1,  # okna plastikowe
               0, 1,  # rynek wtorny
               0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # ródmiecie
               ])

x2 = np.transpose(x2.reshape(-1, 1))
rf.predict(x2)

x3 = np.array([5, 2003, 112, 1, 2003, 1,
               0, 0, 0, 0, 1, 0,  # szeregowiec
               0, 0, 0, 1, 0, 0, 0, 0, 0,  # beton
               0, 0, 0, 1, 0, 0,  # do zamieszkania
               0, 0, 0, 1,  # okna plastikowe
               0, 1,  # rynek wtorny
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,  # łomianki
               ])
x3 = np.transpose(x3.reshape(-1, 1))
rf.predict(x3)  # 7260 zł/m
