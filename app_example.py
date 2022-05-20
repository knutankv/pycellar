from pycellar.interface import create_dash_app
import os

username = ...
password = ...
homey_id = ...

assets_folder = os.getcwd() +'/src'
cellar_dict = dict(username=username, password=password)

webhook_settings = {'normal': dict(homey_id=homey_id,
                      event='finnvin'),
                    'random':dict(homey_id=homey_id,
                                          event='finnvin_random')}

stylesheets = ['style.css', 
               'https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap']
logo_path = 'cellarlogo.png'
icon_paths = dict(red='red_dark.png', 
                   white='white_dark.png', 
                   rose='rose_dark.png', 
                   dessert='dessert_dark.png',
                   sparkling='sparkling_dark.png', 
                   lights_off='lights_off.png', 
                   lights1='lights1.png', 
                   lights2='lights2.png', 
                   ok_consume='ok_consume.png',
                   random='random.png',
                   map_img='map_dark.png',
                   grapes='varietal_dark.png')


app = create_dash_app(cellar_dict, webhook_settings=webhook_settings,
                      assets_folder=assets_folder, stylesheets=stylesheets,
                      logo_path=logo_path, icon_paths=icon_paths)

server = app.server
app.run_server(debug=True)
