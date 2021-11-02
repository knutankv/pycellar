from cellartracker import cellartracker
from getpass import getpass

class Cellar:
    def __init__(self, wines):
        self.wines = wines
    
    @classmethod
    def from_cellartracker_inventory(cls, username, password=None):
        inventory = get_inventory(username, password=password)
        
        cls.wines = []
        
        for wine_dict in inventory:
            cls.wines.append(Wine(wine_dict))
        
        return cls
    
class Wine:
    def __init__(self, wine_dict):
        for key in wine_dict:
            setattr(self, str(key).lower(), wine_dict[key])
        
        
    def __repr__(self):
        return f'{self.vintage} {self.producer} {self.region} {self.designation} ({self.varietal})'
        

def get_inventory(username, password=None):
    if password is None:
        password = getpass('Password: ')
        
    cellar_tracker_client = cellartracker.CellarTracker(username, password)
    
    return cellar_tracker_client.get_inventory()