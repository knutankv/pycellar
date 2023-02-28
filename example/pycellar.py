from pycellar.interface import create_dash_app
import os

username = os.environ['cellartracker_user']
password = os.environ['cellartracker_pwd']
homey_id = os.environ['homey_id']

cellar_dict = dict(username=username, password=password)

webhook_settings = {'normal': dict(homey_id=homey_id,
                      event='finnvin'),
                    'random':dict(homey_id=homey_id,
                                          event='finnvin_random')}

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

app = create_dash_app(cellar_dict, webhook_settings=webhook_settings, icon_paths=icon_paths)
server = app.server


if __name__ == '__main__':
    app.run_server(debug=True)