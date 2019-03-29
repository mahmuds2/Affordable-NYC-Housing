from flask import Flask, render_template
from sodapy import Socrata
import googlemaps
import pandas as pd
import requests
import os

app = Flask(__name__)
client = Socrata("data.cityofnewyork.us", None)
gmaps_token = os.environ['GOOGLE_MAPS_TOKEN']
gmaps = googlemaps.Client(key=gmaps_token)

@app.route('/')
def map():
    # get information on all ntas and nycha buildings
    ntas = client.get("q2z5-ai38")
    nycha = client.get("evjd-dqpz", limit=2,
        select="location_street_a, location_street_b, location_street_c, location_street_d, borough")

    print("nycha:" + str(nycha))
    get_building_nta(nycha)

    # Convert to pandas DataFrame
    ntas_df = pd.DataFrame.from_records(ntas)

    polygons = draw_neighborhoods(ntas_df)
    neighborhoods = get_neighborhood_info(ntas_df)

    return render_template('index.html', polygons=polygons,
                                        neighborhoods=neighborhoods,
                                        gmaps_token=gmaps_token)

def draw_neighborhoods(results):
    '''
    Parameter Type: Pandas DataFrame
    Information of all ntas in NYC

    Return: Dictionary
    Coordinates of all ntas, where key is name and value is array of nta's coordinate path
    '''

    polygons = {}

    for neighborhood in results.iterrows():
        polygons[neighborhood[1]['ntaname']] = get_polygon(neighborhood[1]['the_geom']['coordinates'])

    return polygons

def get_neighborhood_info(results):
    '''
    Parameter Type: Pandas DataFrame
    Set of information of all ntas in NYC

    Return Type: Dictionary
    All nta names and values, where key is name and values are codes
    '''
    neighborhoods = {}

    for neighborhood in results.iterrows():
        neighborhoods[neighborhood[1]['ntaname']] = neighborhood[1]['ntacode']

    return neighborhoods

def get_polygon(neighborhood_coords):
    '''
    Parameter Type: Column of Pandas Dictionary
    All nta coordinates in NYC in format [longitude, latitude]

    Return Type: Array
    Array of tuples containing coordinate path of ntas in format [latitude, longitude]
    '''
    path = []

    for coord in neighborhood_coords[0][0]:
        path.append([coord[0], coord[1]])

    return path

def get_building_nta(address):
    '''
    Parameter Types: String
    Building address

    Return: String
    NTA code of building
    '''
    # get latitude and longtitude of Building
    geocode_result = gmaps.geocode(address)

    for building_info in geocode_result:
        print(str(building_info['formatted_address']), str(building_info['geometry']['location']) + '\n')
