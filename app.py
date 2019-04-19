from flask import Flask, render_template
from sodapy import Socrata
import googlemaps
import pandas as pd
import json
import os

app = Flask(__name__)
client = Socrata("data.cityofnewyork.us", None)
gmaps_token = os.environ['GOOGLE_MAPS_TOKEN']
gmaps = googlemaps.Client(key=gmaps_token)

@app.route('/')
def affordable_units_map():
    # get information on all ntas and nycha buildings
    ntas = client.get("q2z5-ai38")
    affordable_units = client.get("hg8x-zxpr", select="project_id, " +
        "neighborhood_tabulation_area, extremely_low_income_units," +
        "very_low_income_units, low_income_units, latitude, longitude",
        where="extremely_low_income_units > 0 OR very_low_income_units > 0" +
        "OR low_income_units > 0")

    # Convert to pandas DataFrame
    ntas_df = pd.DataFrame.from_records(ntas)

    # data for polygons and information related to each polygon
    polygons = get_all_neighborhoods(ntas_df)
    neighborhoods = get_neighborhood_info(ntas_df)
    violations = get_housing_vio()

    return render_template('index.html', polygons=polygons,
                                        neighborhoods=neighborhoods,
                                        affordable_units=affordable_units,
                                        violations=violations,
                                        gmaps_token=gmaps_token)

@app.route('/nycha')
def nycha_map():
    # Get information on all ntas and nycha buildings
    ntas_df = pd.DataFrame.from_records(client.get("q2z5-ai38"))

    # data for polygons and information related to each polygon
    polygons = get_all_neighborhoods(ntas_df)
    neighborhoods = get_neighborhood_info(ntas_df)
    development = get_nycha_developments()

    return render_template('nycha.html', polygons=polygons,
                                        neighborhoods=neighborhoods,
                                        gmaps_token=gmaps_token)



def get_polygon(coordinates):
    '''
    Parameter Type: Column of Pandas Dictionary, String
     - All polygon coordinates in format [longitude, latitude]
     - String specifying what coordinates draw

    Return Type: Array
     - Array of arrays containing tuples of coordinate path of polygon in format [latitude, longitude]
    '''

    all_polygons = []

    for polygon in coordinates:
        path = []

        for coord in polygon[0]:
            path.append([coord[1], coord[0]])

        all_polygons.append(path)

    return all_polygons

def get_all_neighborhoods(results):
    '''
    Parameter Type: Pandas DataFrame
     - Information of all ntas in NYC

    Return: Dictionary
     - Dictionary containing coordinates of all ntas, where key is nta name and value is array of nta's coordinate path
    '''

    polygons = {}

    for neighborhood in results.iterrows():
        polygons[neighborhood[1]['ntaname']] = get_polygon(neighborhood[1]['the_geom']['coordinates'])

    return polygons

def get_neighborhood_info(results):
    '''
    Parameter Type: Pandas DataFrame
     - Set of information of all ntas in NYC

    Return Type: Dictionary
     - Dictionary of nta names and values, where key is name and values are codes
    '''
    neighborhoods = {}

    for neighborhood in results.iterrows():
        neighborhoods[neighborhood[1]['ntaname']] = neighborhood[1]['ntacode']

    return neighborhoods


def get_nycha_developments():
    '''
    Return Type: Dictionary
     - Dictionary where key is TDS Number and value is array of arrays with coordinates of developments
    '''

    results = client.get("5j2e-zhmb")

    developments = {}

    for development in results:
        developments[development["tds_num"]] = get_polygon(development["the_geom"]["coordinates"])

def get_housing_vio():
    '''
    Return type: Array of JSON objects
    '''
    housing_vios = client.get("b2iz-pps8", select="nta, buildingid, latitude, longitude, class",
                            where="violationstatus = 'Open'")

    return housing_vios
