import dash
from dash import dash_table
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
from pycellar import winelib, lights
from datetime import date
from flask import send_from_directory
import os

def get_wine_types_from_dict(wine_types):
    return [wine_type for wine_type in wine_types if wine_types[wine_type]]

def create_dash_app(cellar, webhook_settings=None, 
                    icon_paths=None, assets_folder='./assets/',
                    table_columns=None):
    
    def filter_cellar(filter_dict):
        def all_filters(wine):    
            vintage_range = filter_dict['vintage_range']
            ok_consume = filter_dict['ok_consume']
            wine_types = filter_dict['wine_types']
            country = filter_dict['country']
            varietal = filter_dict['varietal']
            
            vintage_ok = wine.in_range('vintage', vintage_range)
            consumable_ok = wine.is_consumable() or ~ok_consume
            type_ok = np.any([wt in wine.type.lower() for wt in wine_types])
            country_ok = country is None or (wine.country.lower() == country)
            varietal_ok = varietal is None or (wine.varietal.lower() == varietal.lower())
            ok = vintage_ok and consumable_ok and type_ok and country_ok and varietal_ok
            
            return ok
        
        cellar.filter_wines(all_filters)
    
    def get_sel_wine_bin_and_ix(row):
        wine = cellar.unique_filt_wines[row]

        return wine.bin, wine.iwine
        
    def get_winetable_data(filter_dict, output_columns=False, omit=['id']):
        filter_cellar(filter_dict)
        df = cellar.to_df()[keys]
        df['id'] = df.index
        data = df.to_dict('records') 
        
        if output_columns:
            columns = [{"name": i.capitalize(), "id": i} for i in df.columns if i not in omit]
            return data, columns
        else: 
            return data
    
    app = dash.Dash(__name__, assets_folder=assets_folder)
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    
    if webhook_settings:
        scene_activator = lights.homey_activator(**webhook_settings['normal'])
        if 'random' in webhook_settings:
            scene_activator_random = lights.homey_activator(**webhook_settings['random'])
        else:
            scene_activator_random = scene_activator
    else:
        webhook_settings = webhook_settings['normal']
        scene_activator = lambda x: 0
        scene_activator_random = lambda x: 0
    
    
    if type(cellar) is dict:
        cellar_dict = dict(cellar)
        cellar = winelib.Cellar.from_cellartracker_inventory(cellar_dict['username'], password=cellar_dict['password'])
    
    if table_columns is None:
        keys = ['wine','vintage','bottles']
    else:
        keys = table_columns
    
    # Establish options
    ok_consume = True
    wine_dict = {'red':1, 'white':1, 'rosé':1, 'sparkling':1, 'dessert': 0}
    
    varietals = set(cellar.get_props('varietal'))
    varietals_dashdict = [{'label': var, 
             'value': var} for var in varietals]
        
    
    countries = set(cellar.get_props('country'))
    countries_dashdict = [{'label': reg, 
             'value': reg} for reg in countries]
    
    
    vintage_range = [-np.inf, np.inf]
    filter_dict = dict(wine_types=get_wine_types_from_dict(wine_dict), vintage_range=vintage_range, country=None, varietal=None, ok_consume=ok_consume)
    
    data, columns = get_winetable_data(filter_dict, output_columns=True)

   
    # ------------ LAYOUT ------------
    app.layout = html.Div(className='main', children=
        [html.Div(className='filters', children=[
                html.Div(id='winetypes', children=[
                    html.Img(id='red_type',className='icon', src=app.get_asset_url(icon_paths['red'])),
                    html.Img(id='white_type', className='icon', src=app.get_asset_url(icon_paths['white'])),
                    html.Img(id='rose_type',  className='icon', src=app.get_asset_url(icon_paths['rose'])),
                    html.Img(id='sparkling_type', className='icon', src=app.get_asset_url(icon_paths['sparkling'])),
                    html.Img(id='dessert_type', className='icon', src=app.get_asset_url(icon_paths['dessert']))
                ]),
               
                dcc.RangeSlider(min=2000, max=date.today().year, value=[2000, 2025],
                                id='vintages', tooltip={"placement": "bottom", "always_visible": True}),
                html.Img(id='ok_consume',className='icon', src=app.get_asset_url(icon_paths['ok_consume'])),
                # html.Img(id='random_pick',className='icon', src=app.get_asset_url(icon_paths['random'])),
                
                html.Div(className='iconed_list', children=[
                    html.Img(className='icon', src=app.get_asset_url(icon_paths['map_img'])),
                    dcc.Dropdown(
                        options=countries_dashdict,
                        id='countries', 
                        multi=False,
                        value=None)]),
                html.Div(className='iconed_list', children=[  
                    html.Img(className='icon', src=app.get_asset_url(icon_paths['grapes'])),
                    dcc.Dropdown(
                        options=varietals_dashdict,
                        id='varietals', 
                        multi=False,
                        value=None)
                ]), ]),
            
                html.Div(className='wine_table_container', children=[       
                    dash_table.DataTable(data=data, 
                                          columns=columns, 
                                          id='wine_table', page_size=10, 
                                          style_cell={'textAlign': 'left'}, 
                                          style_table={'width': '100%'}, 
                                          fill_width=False,
                        style_header={
                              'backgroundColor': '#222222',
                              'color': 'white'
                        },
                        style_data={
                            'backgroundColor': 'black',
                            'color': 'white'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'wine'},
                             'width': '10%'}
    ]
                    )]),
            html.Br(),
            html.Div(id='light_controls', children=[
                html.Img(id='lights_off',className='lights-icon', src=app.get_asset_url(icon_paths['lights_off'])),
                html.Img(id='lights1', className='lights-icon', src=app.get_asset_url(icon_paths['lights1'])),
                html.Img(id='lights2',  className='lights-icon', src=app.get_asset_url(icon_paths['lights2'])),
             
            ])
        ])
    

    @app.callback(
        [Output("wine_table", "data"),
         Output("red_type", "style"),
         Output("white_type", "style"),
         Output("rose_type", "style"),
         Output("sparkling_type", "style"),
         Output("dessert_type", "style"),
         Output("ok_consume", "style"),
         Output("wine_table", "active_cell")],
        [Input("vintages", "value"),
         Input("countries", "value"),
         Input("varietals", "value"),
         Input("red_type", "n_clicks"),
         Input("white_type", "n_clicks"),
         Input("rose_type", "n_clicks"),
         Input("sparkling_type", "n_clicks"),
         Input("dessert_type", "n_clicks"),
         Input("ok_consume", "n_clicks")
         ])
    
    def update_table(vintage_range, country, varietal, n_red, n_white, n_rose, n_sparkling,n_dessert,
                     n_ok_consume):

        n_clicks = dict(red=n_red, white=n_white, rosé=n_rose, sparkling=n_sparkling, dessert=n_dessert)
        styles = []
        
        # Establish click values for wine type icons
        for wine_type in ['red','white','rosé','sparkling', 'dessert']:
            n = n_clicks[wine_type]
            
            if n is not None and n % 2 >0:     #odd number
                styles.append({'opacity': 0.3})
                wine_dict[wine_type] = 0
            else:
                styles.append({'opacity': 1.0})
                wine_dict[wine_type] = 1
                
        
        if n_ok_consume is not None and n_ok_consume % 2 > 0:     #odd number
            styles.append({'opacity': 1.0})
            filter_dict['ok_consume'] = True
        else:
            styles.append({'opacity': 0.3})
            filter_dict['ok_consume'] = False
            
        filter_dict['wine_types'] = get_wine_types_from_dict(wine_dict)
        filter_dict['vintage_range'] = vintage_range
        if country is not None:
            country = country.lower()
    
        filter_dict['country'] = country
        filter_dict['varietal'] = varietal
        
        data = get_winetable_data(filter_dict)
        scene_activator('reset_cellar')

        return data, *styles, None
    

    @app.callback(
    Output("lights_off", "style"),
    Input("lights_off", "n_clicks")
    )
    
    def set_lights_off(n):
        scene_activator('lights_off')
    
    @app.callback(
    Output("lights1", "style"),
    Input("lights1", "n_clicks")
    )
    
    def set_lights1(n):
        scene_activator('lights1')
        
        
    @app.callback(
    Output("lights2", "style"),
    Input("lights2", "n_clicks")
    )
    
    def set_lights2(n):
        scene_activator('lights2') 

    @app.callback(
    Output("wine_table", "style_data_conditional"),
    [Input("wine_table", "active_cell"),
     State("lights1", "n_clicks"), State("lights2", "n_clicks"),
     State("lights_off", "n_clicks")]
    )
    
    def sel_wine(active_cell,*args):
        
        if active_cell is None:                                                                                                                                                                                                                      
            val = [
                
            ]  
            scene_activator('reset_cellar')
        else:
            row = active_cell['row']
            sel_bin, iwine = get_sel_wine_bin_and_ix(row)
            scene_activator(sel_bin)
            val = [{
                "if": {"row_index": active_cell.get("row", "")}, 
                  "backgroundColor": "#64889c"}
            ]   
            
        return val

    return app