'''
* https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial
* https://query.wikidata.org/
* https://janakiev.com/blog/wikidata-mayors/

Example call-outs:
  * coordinates_of_voivodeship('województwo podlaskie') -> [53.267219444444, 22.931938888889]
  * coordinates_of_voivodeship('podlaskie')             -> [53.267219444444, 22.931938888889]
'''


# Libraries
import requests
import pandas as pd
from collections import OrderedDict


# Old function
def get_voivodeships_v1():
    # problem - only ten voivodeships has the inception date se
    # solution - version 2 of this function
    
    # request voivodeships of poland(wd:Q36)
    # https://query.wikidata.org/#%20%20%20%20SELECT%20%3Fvoivodeship%20%3FvoivodeshipLabel%20%3Finception%20%3Flocation%0A%20%20%20%20WHERE%20%7B%0A%20%20%20%20%20%20%3Fvoivodeship%20wdt%3AP31%20wd%3AQ150093%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wdt%3AP571%20%3Finception%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wdt%3AP625%20%3Flocation.%0A%20%20%20%20%20%20FILTER%28%3Finception%20%3E%3D%20%221999-01-01%22%5E%5Exsd%3AdateTime%29.%0A%0A%20%20%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%0A%20%20%20%20%7D
    url = 'https://query.wikidata.org/sparql'
    query = '''
    SELECT ?voivodeship ?voivodeshipLabel ?inception ?location
    WHERE {
      ?voivodeship wdt:P31 wd:Q150093;
                   wdt:P571 ?inception;
                   wdt:P625 ?location.
      FILTER(?inception >= "1999-01-01"^^xsd:dateTime).

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    '''
    r = requests.get(url, params = {'format': 'json', 'query': query})
    data = r.json()

    # convert json to dataframe
    voivodeships = []
    for item in data['results']['bindings']:
        voivodeships.append(OrderedDict(
        {
            'voivodeship':      item['voivodeshipLabel']['value'],
            'location':         item['location']['value'],        
            'wikidata_item_id': item['voivodeship']['value'].split('/')[-1]
        }))
    #     print(item,'\n')

    df = pd.DataFrame(voivodeships)
    return df


# Correct function
def get_voivodeships_v2():
    # problem - too many voivodeships, historical ones are mixed together
    # solution - just cut the list after 16-th item
    
    # request voivodeships of poland(wd:Q36)
    # cut after 16 voivodeships, the rest are historical ones
    # https://query.wikidata.org/#SELECT%20%3Fvoivodeship%20%3FvoivodeshipLabel%20%3Flatitude%20%3Flongitude%20%3Fadmininistrative_teritorial_entity%0AWHERE%20%7B%0A%20%20%3Fvoivodeship%20wdt%3AP31%20wd%3AQ150093%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wdt%3AP131%20%3Fadmininistrative_teritorial_entity%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20p%3AP625%2Fpsv%3AP625%20%5B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLatitude%20%3Flatitude%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3AgeoLongitude%20%3Flongitude%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5D.%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%0A%20%20FILTER%28%3Fadmininistrative_teritorial_entity%20%3D%20wd%3AQ36%29.%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22pl%22.%20%7D%0A%7D%0AORDER%20BY%20DESC%28%3Fvoivodeship%29%0ALIMIT%2016
    # https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Mountains
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
            'voivodeship':      item['voivodeshipLabel']['value'],
            'latitude':         float(item['latitude']['value']),        
            'longitude':         float(item['longitude']['value']),                    
            'wikidata_item_id': item['voivodeship']['value'].split('/')[-1]
        }))
    #     print(item,'\n')    
    
    df = pd.DataFrame(voivodeships)
    return df


def coordinates_of_voivodeship(wojewodztwo):
    voivodeships = get_voivodeships_v2()
    coordinates = voivodeships.loc[voivodeships['voivodeship'].str.contains(wojewodztwo) == True, ['latitude', 'longitude']]
    return coordinates.values.tolist()[0]