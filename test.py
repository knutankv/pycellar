from cellartracker import cellartracker
from getpass import getpass

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

from pycellar import winelib
from pycellar.interface import create_dash_app

username = input('Username: ')
password = getpass('Password: ')
# password = 'minvin'
# username = 'knut.a.kvale@gmail.com'

image_path = 'C:/Users/knutankv/git-repos/pycellar/cellarimage.png'

bin_dict = dict(
    A1=[183, 484],
    A2=[183, 555],
    A3=[183, 622],
    A4=[183, 667],
    A5=[183, 745],

    B1=[220, 370],
    B2=[220, 445],
    B3=[220, 514],
    B4=[220, 580],
    B5=[220, 634],

    C1=[291, 289],
    C2=[291, 359],
    C3=[291, 434],
    C4=[291, 497],
    C5=[291, 559],

    D1=[451, 287],
    D2=[451, 356],
    D3=[451, 424],
    D4=[451, 488],
    D5=[451, 546],

    E1=[569, 316],
    E2=[569, 386],
    E3=[569, 447],
    E4=[569, 515],
    E5=[569, 575])

cellar_dict = dict(username=username, password=password)

app = create_dash_app(cellar_dict, image_path=image_path, bin_dict=bin_dict)
server = app.server


app.run_server(port=8080, host='192.168.100.3', debug=False)
