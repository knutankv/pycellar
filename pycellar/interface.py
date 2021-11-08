import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
from skimage import io
import numpy as np
from pycellar import winelib

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_dash_app(cellar, image_path=None, bin_dict=None):
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    
    if image_path is not None:
        img = io.imread(image_path)
    else:
        img = None

    fig = px.imshow(img)
    if type(cellar) is dict:
        cellar_dict = dict(cellar)
        cellar = winelib.Cellar.from_cellartracker_inventory(cellar_dict['username'], password=cellar_dict['password'])
        update_cellar_bool = True
    else:
        update_cellar_bool = False
    
    # ------------ LAYOUT ------------
    app.layout = html.Div(className='main', children=
        [       

            dcc.Dropdown(
                options=cellar.get_dash_dict(),
                id='selected_wines',
                multi=True,
                value="MTL"),
            html.Button('Oppdatér', id='oppdater_btn', n_clicks=0),
            html.Div(id='hidden-div', style={'display':'none'}),
            dcc.Graph(figure=fig, id='cellarimg', 
                      style={'width': '90vh', 'height': '90vh'}),
            
        ])
    
    
    @app.callback(
    dash.dependencies.Output('selected_wines', 'options'),
    [dash.dependencies.Input('oppdater_btn', 'n_clicks')])
    
    def update_cellar(n_clicks):
        if update_cellar_bool:
            cellar = winelib.Cellar.from_cellartracker_inventory(cellar_dict['username'], password=cellar_dict['password'])
            return cellar.get_dash_dict()
    
    @app.callback(
    dash.dependencies.Output('cellarimg', 'figure'),
    [dash.dependencies.Input('selected_wines', 'value')])
    
    def highlight_bins(selected_wines):
        wines = cellar.wines_from_barcodes(selected_wines)
        bin_coors = [bin_dict[wine.bin] for wine in wines]
        fig.data = [fig.data[0]]
        
        if bin_coors != []:       
            bin_coors = np.vstack(bin_coors)
            markers = fig.add_trace(go.Scatter(x=bin_coors[:,0], y=bin_coors[:,1], mode='markers'))

        return fig
    
    return app
