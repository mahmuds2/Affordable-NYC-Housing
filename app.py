from flask import Flask, render_template
from sodapy import Socrata
import pandas as pd
import os

app = Flask(__name__)
client = Socrata("data.cityofnewyork.us", None)
gmaps_token = os.environ['GOOGLE_MAPS_TOKEN']

@app.route('/')
def map():
    polygons = draw_neighborhoods()

    return render_template('index.html', polygons=polygons, gmaps_token=gmaps_token)

def draw_neighborhoods():
    '''
    Return: Array of strings representing coordinates of neighborhood outline
    '''

    # First 2000 results, returned as JSON from API / converted to Python list of
    # dictionaries by sodapy.
    results = client.get("q2z5-ai38", limit=200)

    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)

    polygons = []

    print(results_df['ntaname'])
    for neighborhood in results_df['the_geom']:
        polygons.append(get_polygon(neighborhood['coordinates']))

    return polygons

def get_polygon(neighborhood_coords):
    path = []

    for coord in neighborhood_coords[0][0]:
        path.append([coord[0], coord[1]])

    return path
