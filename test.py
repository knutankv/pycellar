from cellartracker import cellartracker
from getpass import getpass

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# password = getpass('Password: ')
password = 'minvin'
username = 'knut.a.kvale@gmail.com'

client = cellartracker.CellarTracker(username, password)

client.get_list()           # Return List
client.get_inventory()      # Return Inventory
     
inventory = client.get_inventory()
lst = client.get_list()

