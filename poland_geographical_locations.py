# Info
'''
* https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial
* https://query.wikidata.org/
* https://janakiev.com/blog/wikidata-mayors/
* https://en.wikibooks.org/wiki/SPARQL/WIKIDATA_Precision,_Units_and_Coordinates#Coordinates
* https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Mountains
'''

# Imports
import requests
import pandas as pd
from collections import OrderedDict
import numpy as np


# Defs
def get_voivodeships():
    # problem - too many voivodeships, historical ones are mixed together
    # solution - just cut the list after 16-th item
    
    # request voivodeships of poland(wd:Q36),
    # cut after 16 voivodeships, the rest are historical ones
    # https://query.wikidata.org/#%20%20%20%20SELECT%20%3Fvoivodeship%20%3FvoivodeshipLabel%20%3Flatitude%20%3Flongitude%20%3Fadmininistrative_teritorial_entity%0A%20%20%20%20WHERE%20%7B%0A%20%20%20%20%20%20%3Fvoivodeship%20wdt%3AP31%20wd%3AQ150093%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wdt%3AP131%20%3Fadmininistrative_teritorial_entity%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20p%3AP625%2Fpsv%3AP625%20%5B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLatitude%20%3Flatitude%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLongitude%20%3Flongitude%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5D.%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20FILTER%28%3Fadmininistrative_teritorial_entity%20%3D%20wd%3AQ36%29.%0A%20%20%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22pl%22.%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20ORDER%20BY%20DESC%28%3Fvoivodeship%29%0A%20%20%20%20LIMIT%2016%0A
    url = 'https://query.wikidata.org/sparql'
    query = '''
    SELECT ?voivodeship ?voivodeshipLabel ?latitude ?longitude ?admininistrative_teritorial_entity
    WHERE {
      ?voivodeship wdt:P31 wd:Q150093;
                   wdt:P131 ?admininistrative_teritorial_entity;
                   p:P625/psv:P625 [
                       wikibase:geoLatitude ?latitude ;
                       wikibase:geoLongitude ?longitude ;
                   ].               
      FILTER(?admininistrative_teritorial_entity = wd:Q36).
      SERVICE wikibase:label { bd:serviceParam wikibase:language "pl". }
    }
    ORDER BY DESC(?voivodeship)
    LIMIT 16
    '''
    r = requests.get(url, params = {'format': 'json', 'query': query})
    data = r.json()

    # convert json to dataframe
    voivodeships = []
    for item in data['results']['bindings']:
        voivodeships.append(OrderedDict(
        {
            'voivodeship':      item['voivodeshipLabel']['value'].lower(),
            'latitude':         float(item['latitude']['value']),        
            'longitude':        float(item['longitude']['value']),                    
            'wikidata_item_id': item['voivodeship']['value'].split('/')[-1]
        }))
    #     print(item,'\n')    
    
    df = pd.DataFrame(voivodeships)
    return df

voivodeships = get_voivodeships()
voivodeships


def get_warsaw_districts():
    # problem  - some districts have two sets of coordinates
    # solution - drop the one with worse precision (larger value), this seems to be consistent with the wikipedia data
    
    # https://query.wikidata.org/#SELECT%20%3Fdistrict_of_Warsaw%20%3Fdistrict_of_WarsawLabel%20%3Flat%20%3Flon%20%3FgeoPrecision%20%0AWHERE%20%7B%0A%20%20%3Fdistrict_of_Warsaw%20%20wdt%3AP31%20wd%3AQ4286337%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wdt%3AP17%20wd%3AQ36%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wdt%3AP131%20wd%3AQ270%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20p%3AP625%2Fpsv%3AP625%20%5B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLatitude%20%3Flat%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLongitude%20%3Flon%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoPrecision%20%20%3FgeoPrecision%3B%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5D%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22pl%22.%20%7D%0A%7D
    url = 'https://query.wikidata.org/sparql'
    query = '''
    SELECT ?warsaw_district ?warsaw_districtLabel ?latitude ?longitude ?geoPrecision 
    WHERE {
      ?warsaw_district  wdt:P31 wd:Q4286337;
                        wdt:P17 wd:Q36;
                        wdt:P131 wd:Q270;
                        p:P625/psv:P625 [
                            wikibase:geoLatitude ?latitude ;
                            wikibase:geoLongitude ?longitude ;
                            wikibase:geoPrecision  ?geoPrecision;                                       
                        ]
      SERVICE wikibase:label { bd:serviceParam wikibase:language "pl". }
    }
    ORDER BY ASC(?warsaw_districtLabel)
    '''
    r = requests.get(url, params = {'format': 'json', 'query': query})
#     print(r.json())
    data = r.json()

    # convert json to dataframe
    warsaw_districts = []
    for item in data['results']['bindings']:
#         print(item,'\n')    
        warsaw_districts.append(OrderedDict(
        {
            'warsaw_district':  item['warsaw_districtLabel']['value'].lower(),
            'latitude':         float(item['latitude']['value']),        
            'longitude':        float(item['longitude']['value']),                    
            'geoPrecision':     float(item['geoPrecision']['value']),                                
            'wikidata_item_id': item['warsaw_district']['value'].split('/')[-1]
        }))
    
    warsaw_districts = pd.DataFrame(warsaw_districts).sort_values(by=['warsaw_district'])
    
    # if duplicate warsaw districts exist, take the one with better precision (lower value), do the opposite in case of 'Wola' 
    for district in warsaw_districts['warsaw_district']:
        if np.sum(warsaw_districts['warsaw_district'] == district) > 1: # duplicate district found
            if district != 'wola':            
                district_to_drop_idx = warsaw_districts.loc[warsaw_districts['warsaw_district'] == district, 'geoPrecision'].idxmax()
            elif district == 'wola':
                district_to_drop_idx = warsaw_districts.loc[warsaw_districts['warsaw_district'] == district, 'geoPrecision'].idxmin()
#             print(district+':\t', district_to_drop_idx, '\n')
            warsaw_districts = warsaw_districts.drop(district_to_drop_idx).reset_index(drop=True)  
            
    return warsaw_districts

warsaw_districts = get_warsaw_districts()
warsaw_districts



def get_cities():
    # Description:
    #  - sparql query is constructed for different types of cities: city with powiat rights ('Q925381'), urban municipality of Poland (Q2616791), and the second for "regular" city ('Q515')
    # Problems:
    #   1) some cities have more than one set of coordinates
    #   2) filter within masovian voivodeship
    # Solutions:
    #   1) retain only the one with best precision (lowest value)
    #   2) we can use .contains method from geopandas package, check the crs of Point from wikidata (https://www.kaggle.com/alexisbcook/proximity-analysis)
    # To do:
    #   1) check this approach
      
    # Get both types of cities: cities with powiat rights (Q925381), urban municipality of Poland (Q2616791), and the the "regular" cities (Q515)
    # https://docs.python.org/3/reference/lexical_analysis.html#f-strings
    # https://query.wikidata.org/#SELECT%20%3Fcity%20%3FcityLabel%20%3Flatitude%20%3Flongitude%20%3FgeoPrecision%20%3Fcoord%0AWHERE%20%7B%0A%20%20%3Fcity%20%20wdt%3AP31%20wd%3AQ925381%3B%0A%20%20%20%20%20%20%20%20%20wdt%3AP17%20wd%3AQ36%3B%0A%20%20%20%20%20%20%20%20%20%23wdt%3AP131%20wd%3AQ54169%3B%0A%20%20%20%20%20%20%20%20%20p%3AP625%20%5B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20psv%3AP625%20%5B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLatitude%20%3Flatitude%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLongitude%20%3Flongitude%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoPrecision%20%20%3FgeoPrecision%3B%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5D%3B%0A%20%20%20%20%20%20%20%20%20ps%3AP625%20%3Fcoord%20%0A%20%20%20%20%20%20%20%20%20%5D%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22pl%22.%20%7D%0A%7D
    # https://query.wikidata.org/#SELECT%20%3Fcity%20%3FcityLabel%20%3Flatitude%20%3Flongitude%20%3FgeoPrecision%20%3Fcoord%0AWHERE%20%7B%0A%20%20%3Fcity%20%20wdt%3AP31%20wd%3AQ515%3B%0A%20%20%20%20%20%20%20%20%20wdt%3AP17%20wd%3AQ36%3B%0A%20%20%20%20%20%20%20%20%20%23wdt%3AP131%20wd%3AQ54169%3B%0A%20%20%20%20%20%20%20%20%20p%3AP625%20%5B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20psv%3AP625%20%5B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLatitude%20%3Flatitude%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLongitude%20%3Flongitude%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoPrecision%20%20%3FgeoPrecision%3B%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5D%3B%0A%20%20%20%20%20%20%20%20%20ps%3AP625%20%3Fcoord%20%0A%20%20%20%20%20%20%20%20%20%5D%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22pl%22.%20%7D%0A%7D
    cities_all = pd.DataFrame()
    url = 'https://query.wikidata.org/sparql'
    data = pd.DataFrame()
    types_of_city = {'city with powiat rights': 'Q925381', 'urban municipality of Poland ': 'Q2616791', 'city': 'Q515'}
    for type_of_city, type_of_city_sparql in types_of_city.items():
#         print('\n\nCities of type \'' + type_of_city + '\' (' + str(type_of_city_sparql) + '):')
        query = f''' 
            SELECT ?city ?cityLabel ?latitude ?longitude ?geoPrecision ?coord
            WHERE {{
              ?city  wdt:P31 wd:{type_of_city_sparql};
                     wdt:P17 wd:Q36;
                     #wdt:P131 wd:Q54169;
                     p:P625 [
                             psv:P625 [
                                       wikibase:geoLatitude ?latitude ;
                                       wikibase:geoLongitude ?longitude ;
                                       wikibase:geoPrecision  ?geoPrecision;      
                                      ];
                     ps:P625 ?coord 
                     ]
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl". }}
            }}
            '''
        r = requests.get(url, params = {'format': 'json', 'query': query})
        data = r.json()

        
        # Convert json to dataframe
        cities = []
        for item in data['results']['bindings']:
#             print(item,'\n')    
            cities.append(OrderedDict(
            {
                'city':             item['cityLabel']['value'].lower(),
                'latitude':         float(item['latitude']['value']),        
                'longitude':        float(item['longitude']['value']),                    
                'geoPrecision':     float(item['geoPrecision']['value']),                                
                'wikidata_item_id': item['city']['value'].split('/')[-1]
            }))
        cities = pd.DataFrame(cities).sort_values(by=['city']).reset_index(drop=True)
#         print('Number of cities of type', type_of_city+':', len(cities))

        
        # Find those city names that have multiple instaces:
        #   - those with the same wikidata_item_id are the same city with multiple coordinate sets - retain only the set with best (lowest) geoPrecision,
        #   - those with different wikidata_item_id are different cities and should not be considered with the following procedure.
        # https://stackoverflow.com/questions/55360314/pandas-groupby-take-counts-greater-than-1
        cities_with_the_same_name_and_wikidataItemId = cities.loc[cities.groupby(['city', 'wikidata_item_id'])['geoPrecision'].transform('count') > 1].reset_index(drop=True) # cities.loc[cities.duplicated(subset=['city', 'wikidata_item_id'], keep=False)].reset_index(drop=True)
#         print('Cities with the same name and the same wikidata_item_id:', len(cities_with_the_same_name_and_wikidataItemId))
        
    
        # If multiple instances of any city exist, retain only the one with the best precision (lowest value) 
#         print('Cities with multiple instances:', len(cities_with_the_same_name_and_wikidataItemId), '\n')
        for city in cities_with_the_same_name_and_wikidataItemId['city'].unique():
#             print(city)
            city_to_retain_idx = cities_with_the_same_name_and_wikidataItemId.loc[cities_with_the_same_name_and_wikidataItemId['city'] == city, 'geoPrecision'].idxmin()        
            cities_to_drop = cities_with_the_same_name_and_wikidataItemId.loc[(cities_with_the_same_name_and_wikidataItemId['city'] == city) & (cities_with_the_same_name_and_wikidataItemId.index != city_to_retain_idx)].index
#             print('city:', city, '\nindex and geoPrecision of instance to retain:', city_to_retain_idx, cities_with_the_same_name_and_wikidataItemId.loc[city_to_retain_idx, 'geoPrecision'], '\nindices and geoPrecisions of instances to drop:\n', tabulate(cities_with_the_same_name_and_wikidataItemId.loc[cities_to_drop, ['geoPrecision']], tablefmt='psql'))
            cities = cities.drop(cities_to_drop).reset_index(drop=True)
#         print('Number of cities with multiple instances of given cities after cleaning:', len(cities_with_the_same_name_and_wikidataItemId))


        # Append to cities_all
        cities_all = pd.concat([cities_all, cities], axis = 0).sort_values(by=['city']).reset_index(drop=True)
#         print('Number of cities of type', type_of_city, 'after cleaning duplicate coordinates:', len(cities))

    
#     print('Number of all cities:', len(cities_all), '\n', '#'*72)
    return cities_all

cities = get_cities()
cities



def return_coordinates(place):
    '''
    Returns coordinates of the place.
        The place must be the name (in polish) of voivodeship in Poland or the district of Warsaw.
    E.g.:
      1)
        In:  return_coordinates('województwo podlaskie')
        Out: [53.267219444444, 22.931938888889]
      2) 
        In:  return_coordinates('podlaskie')
        Out: [53.267219444444, 22.931938888889]
      3)
        In:  return_coordinates('PODLASKIE')
        Out: [53.267219444444, 22.931938888889]
      4) 
        In:  return_coordinates('Ursus')
        Out: [52.19517, 20.88419] 
      5) 
        In:  return_coordinates('Dobra')
        Out: [53.583333333333, 15.308333333333] 
      6) 
        In:  return_coordinates('żyrardów')
        Out: [52.05, 20.433333333333]       
    '''
    
    coordinates = [None, None]
    place = place.lower()
    
    try:
        voivodeships = get_voivodeships()
        coordinates_df = voivodeships.loc[voivodeships['voivodeship'].str.contains(place) == True, ['latitude', 'longitude']]
        coordinates = coordinates_df.values.tolist()[0]       
    except IndexError:
        try:
            warsaw_districts = get_warsaw_districts()
            coordinates_df = warsaw_districts.loc[warsaw_districts['warsaw_district'].str.contains(place) == True, ['latitude', 'longitude']]
            coordinates = coordinates_df.values.tolist()[0]
        except IndexError:    
            try:
                cities = get_cities()
                coordinates_df = cities.loc[cities['city'].str.contains(place) == True, ['latitude', 'longitude']]
                coordinates = coordinates_df.values.tolist()[0]
            except IndexError:
                pass     
        
    return coordinates

# user_place = input("Podaj województwo, miasto albo dzielnicę Warszawy:")
# c = return_coordinates(user_place)
# print(c)