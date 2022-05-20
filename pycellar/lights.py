import requests

def homey_activator(homey_id, event):
    def webhook_getter(scene):
        url = f'https://{homey_id}.connect.athom.com/api/manager/logic/webhook/{event}?tag={scene}'
        requests.get(url)
        
    return webhook_getter