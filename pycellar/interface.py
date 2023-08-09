import dash
from dash import dash_table, html
from dash.dependencies import Output, Input, State
from dash import dcc

import datetime
today = datetime.date.today()
year = today.year

import numpy as np
from pycellar import winelib, lights
from datetime import date


def zerofy_dict(d):
    dzero = {key:0 for key in d if d[key] is None}
    d.update(dzero)
    
    return d

def get_wine_types_from_dict(wine_types):
    return [wine_type for wine_type in wine_types if wine_types[wine_type]]

def create_dash_app(nm, cellar, webhook_settings=None, 
                    icon_paths=None, table_columns=None, list_inventory=True, **kwargs):
    

    def get_sel_wine_bin_and_ix(row):
        wine = cellar.unique_filt_wines[row]

        return wine.bin, wine.iwine
    
    def get_winetable_columns(df, omit=['id']):
        columns = [{"name": i.capitalize(), "id": i} for i in df.columns if i not in omit]
        return columns
    
    def get_df(cellar, filter_dict, sel_keys=None):
        if sel_keys is None:
            sel_keys = keys*1
            
        def all_filters(wine):    
            vintage_range = filter_dict['vintage_range']
            ok_consume = filter_dict['ok_consume']
            wine_types = filter_dict['wine_types']
            country = filter_dict['country']
            varietal = filter_dict['varietal']
            
            vintage_ok = wine.in_range('_vintage', vintage_range)
            consumable_ok = wine.is_consumable() or ~ok_consume
            type_ok = np.any([wt in wine.type.lower() for wt in wine_types])
            country_ok = country is None or (wine.country.lower() == country)
            varietal_ok = varietal is None or (wine.varietal.lower() == varietal.lower())
            ok = vintage_ok and consumable_ok and type_ok and country_ok and varietal_ok
            
            return ok
        
        cellar.filter_wines(all_filters)
        df = cellar.to_df()[sel_keys]
        df['id'] = df.index
        
        return df
    
    app = dash.Dash(nm, **kwargs)


    if webhook_settings:
        scene_activator = lights.homey_activator(**webhook_settings['normal'])
        if 'random' in webhook_settings:
            scene_activator_random = lights.homey_activator(**webhook_settings['random'])
        else:
            scene_activator_random = scene_activator
    else:
        webhook_settings = webhook_settings['normal']
        scene_activator = lambda x: 0
    
    if type(cellar) is dict:
        cellar_dict = dict(cellar)
        cellar = winelib.Cellar.from_cellartracker_inventory(cellar_dict['username'], password=cellar_dict['password'])
    
    if table_columns is None:
        keys = ['wine','vintage','bottles']
    else:
        keys = table_columns
    
    # Establish options
    ok_consume = True
    wine_dict = {'red':1, 'white':1, 'rosé':1, 'sparkling':1, 'dessert': 1}
    
    varietals = set(cellar.get_props('varietal'))
    varietals_dashdict = [{'label': var, 
             'value': var} for var in varietals]
        
    
    countries = set(cellar.get_props('country'))
    countries_dashdict = [{'label': reg, 
             'value': reg} for reg in countries]
    
    
    vintage_range = [-np.inf, np.inf]
    filter_dict = dict(wine_types=get_wine_types_from_dict(wine_dict), 
                       vintage_range=vintage_range, country=None, varietal=None, ok_consume=ok_consume)
    
    df = get_df(cellar, filter_dict)
    data = df.to_dict('records')
    columns = get_winetable_columns(df)
   
    # ------------ LAYOUT ------------
    app.layout = html.Div(className='main', children=
        [html.Div(className='filters', children=[
                html.Div(id='winetypes', children=[
                    html.Img(src=dash.get_asset_url(icon_paths['red']), id='red_type',className='icon'),
                    html.Img(id='white_type', className='icon', src=dash.get_asset_url(icon_paths['white'])),
                    html.Img(id='rose_type',  className='icon', src=dash.get_asset_url(icon_paths['rose'])),
                    html.Img(id='sparkling_type', className='icon', src=dash.get_asset_url(icon_paths['sparkling'])),
                    html.Img(id='dessert_type', className='icon', src=dash.get_asset_url(icon_paths['dessert']))
                ]),
               
                dcc.RangeSlider(min=year-20, max=year, step=1, marks={i: '{}'.format(i) for i in range(year-20,year+1,2)},
                                id='vintages', tooltip={"placement": "bottom", "always_visible": True}),
                html.Img(id='ok_consume',className='icon', src=dash.get_asset_url(icon_paths['ok_consume'])),

                html.Div(className='iconed_list', children=[
                    html.Img(className='icon', src=dash.get_asset_url(icon_paths['map_img'])),
                    dcc.Dropdown(
                        options=countries_dashdict,
                        id='countries', 
                        multi=False,
                        value=None)]),
                html.Div(className='iconed_list', children=[  
                    html.Img(className='icon', src=dash.get_asset_url(icon_paths['grapes'])),
                    dcc.Dropdown(
                        options=varietals_dashdict,
                        id='varietals', 
                        multi=False,
                        value=None)
                ]), ]),
            
                html.Div(className='wine_table_container', children=[       
                    dash_table.DataTable(data=data, 
                                          columns=columns, 
                                          id='wine_table', page_size=5, 
                                          style_cell={'textAlign': 'left', 'color': 'white'},
                        style_header={
                              'backgroundColor': '#303030',
                              'color': 'white'
                        },
                        style_data={
                            'backgroundColor': '#303030',
                            'color': 'white',
                            'border': 'none'
                        },
                        style_as_list_view=True,
                        style_cell_conditional=[
                            {'if': {'column_id': 'wine'},
                             'width': '10%'}
    ]
                    )]),
            html.Br(),
            html.Div(id='light_controls', children=[
                html.Img(id='lights_off',className='lights-icon', src=dash.get_asset_url(icon_paths['lights_off'])),
                html.Img(id='lights1', className='lights-icon', src=dash.get_asset_url(icon_paths['lights1'])),
                html.Img(id='lights2',  className='lights-icon', src=dash.get_asset_url(icon_paths['lights2'])),
             
            ]),
            html.Div(children=[html.H2(f'# {len(cellar.wines)}')]),
            html.H3(' ', id='bin_text'),
            dcc.Store(data={"red": 0, "white":0, "rosé":0, "sparkling":0, "dessert":0}, 
                     id='clicks'),
            dcc.Store(data=wine_dict, 
                     id='active')
        ])
    

    @app.callback(
        [Output("wine_table", "data"),
         Output("countries", "options"),
         Output("varietals", "options"),
         Output("red_type", "style"),
         Output("white_type", "style"),
         Output("rose_type", "style"),
         Output("sparkling_type", "style"),
         Output("dessert_type", "style"),
         Output("ok_consume", "style"),
         Output("wine_table", "active_cell"),
         Output("clicks", "data"),
         Output("active", "data")],
        [Input("vintages", "value"),
         Input("countries", "value"),
         Input("varietals", "value"),
         Input("red_type", "n_clicks"),
         Input("white_type", "n_clicks"),
         Input("rose_type", "n_clicks"),
         Input("sparkling_type", "n_clicks"),
         Input("dessert_type", "n_clicks"),
         Input("ok_consume", "n_clicks"),
         Input("clicks", "data"),
         Input("active", "data")
         ])
    
    def update_table(vintage_range, country, varietal,
                     n_red, n_white, n_rose, n_sparkling, n_dessert, n_ok_consume,
                     all_clicks, all_active):
        
        order_output = ['red', 'white', 'rosé', 'sparkling', 'dessert']
        
        n_clicks = {'red':n_red,
                    'white':n_white, 
                    'rosé':n_rose,
                    'sparkling':n_sparkling, 
                    'dessert':n_dessert}
        
        n_clicks = zerofy_dict(n_clicks)
        styles = [{'opacity': all_active[wt]} for wt in all_active]
        all_is_active = all(all_active.values())
        
        # Establish click values for wine type icons
        for wine_type in all_clicks:
            if n_clicks[wine_type] > all_clicks[wine_type]:
                all_clicks[wine_type] = n_clicks[wine_type]
                if all_active[wine_type] == 1 and not all_is_active:
                    all_active = {wt: 1 for wt in order_output}
                    styles = [{'opacity': 1.0}] * len(order_output)
                else:
                    all_active = {wt: 0 for wt in order_output}
                    all_active[wine_type] = 1
                    styles = [{'opacity': 0.3}] * len(order_output)
                    styles[order_output.index(wine_type)] = {'opacity': 1}

                break
            
                
        if n_ok_consume is not None and n_ok_consume % 2 > 0:     #odd number
            styles.append({'opacity': 1.0})
            filter_dict['ok_consume'] = True
        else:
            styles.append({'opacity': 0.3})
            filter_dict['ok_consume'] = False
            
        filter_dict['wine_types'] = get_wine_types_from_dict(all_active)
        filter_dict['vintage_range'] = vintage_range
        
        if country is not None:
            country = country.lower()
    
        filter_dict['country'] = country
        filter_dict['varietal'] = varietal

        data_full = get_df(cellar, filter_dict, sel_keys=keys)
        # df_add = data_full[['varietal']]

        data = data_full.to_dict('records')
        
        # varietals = set(df_add['varietal'].values)
        # varietals_dashdict = [{'label': var, 
        #          'value': var} for var in varietals]
            
        # countries = set(df_add['region'].values)
        # countries_dashdict = [{'label': reg, 
                 # 'value': reg} for reg in countries]
        
        scene_activator('reset_cellar')

        return data, countries_dashdict, varietals_dashdict, *styles, None, all_clicks, all_active
    

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
    [Output("wine_table", "style_data_conditional"), Output("bin_text", "children")],
    [Input("wine_table", "active_cell"),Input("wine_table", "data"),
     State("lights1", "n_clicks"), State("lights2", "n_clicks"),
     State("lights_off", "n_clicks")]
    )
    
    def sel_wine(active_cell, data, *args):
        
        if active_cell is None:                                                                                                                                                                                                                      
            val = [
                
            ]  
            scene_activator('reset_cellar')
            text_out = ''
        else:
            iwine = active_cell['row_id']
            wine = cellar.get_wine(iwine)
            text_out = f'{wine.wine}: {wine.bin}'
            
            scene_activator(wine.bin)
            val = [{
                "if": {"row_index": active_cell.get("row", "")}, 
                  "backgroundColor": "#64889c"}
            ]   
            
        return val, text_out

    return app