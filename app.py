from flask import Flask, render_template
from sodapy import Socrata
import pandas as pd
import os

app = Flask(__name__)
client = Socrata("data.cityofnewyork.us", None)
gmaps_token = os.environ['GOOGLE_MAPS_TOKEN']

@app.route('/')
def map():
    # First 2000 results, returned as JSON from API / converted to Python list of
    # dictionaries by sodapy.
    results = client.get("q2z5-ai38", limit=200)

    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)

    polygons = draw_neighborhoods(results_df)
    neighborhoods = get_neighborhood_info(results_df)

    return render_template('index.html', polygons=polygons,
                                        neighborhoods=neighborhoods,
                                        gmaps_token=gmaps_token)

def draw_neighborhoods(results):
    '''
    Return: Dictionary where key is nta name and value is array of coordinate path of neighborhood
    '''

    polygons = {}

    print(results.columns)
    for neighborhood in results.iterrows():
        polygons[neighborhood[1]['ntaname']] = get_polygon(neighborhood[1]['the_geom']['coordinates'])

    return polygons

def get_neighborhood_info(results):
    '''
    Return: Dictionary where key is nta name and values are nta codes
    '''
    neighborhoods = {}

    for neighborhood in results.iterrows():
        neighborhoods[neighborhood[1]['ntaname']] = neighborhood[1]['ntacode']

    return neighborhoods

def get_polygon(neighborhood_coords):
    path = []

    for coord in neighborhood_coords[0][0]:
        path.append([coord[0], coord[1]])

    return path
