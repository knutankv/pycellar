from cellartracker import cellartracker
from getpass import getpass
import re

class Cellar:
    def __init__(self, wines):
        self.wines = wines
    
        
    def get_wine_dict(self):
        return {wine.barcode: wine.full_name for wine in self.wines}
    
    def get_dash_dict(self):
        return [{'label': wine.full_name, 
                 'value': wine.barcode} for wine in self.wines] 
    
    def wines_from_barcode(self, barcode):
        barcodes = [wine.barcode for wine in self.wines]
        
        ix = [i for i, x in enumerate(barcodes) if x == barcode]
        wines = [self.wines[this_ix] for this_ix in ix]
        return wines
        
    def wines_from_barcodes(self, barcodes):
        all_wines = [self.wines_from_barcode(bc) for bc in barcodes]
        all_wines_flattened = [i for j in all_wines for i in j]
        return all_wines_flattened
        
    @classmethod
    def from_cellartracker_inventory(cls, username, password=None):
        inventory = get_inventory(username, password=password)
        
        wines = []
        
        for wine_dict in inventory:
            wines.append(Wine(wine_dict))
            
        
        
        return cls(wines)
    

class Wine:
    def __init__(self, wine_dict):
        for key in wine_dict:
            setattr(self, str(key).lower(), wine_dict[key])
        
        self.barcode = int(self.barcode)
        
    @property
    def full_name(self):
        return f'{self.vintage} {self.producer} {self.appellation} ({self.region} {self.varietal})'
    
    def __repr__(self):
        return self.full_name
        

def get_inventory(username, password=None):
    if password is None:
        password = getpass('Password: ')
        
    cellar_tracker_client = cellartracker.CellarTracker(username, password)
    
    return cellar_tracker_client.get_inventory()

def convert_bin_to_coordinates(this_bin):
    parts = re.split('(\d.*)','this_bin') 
    column = parts[0]
    row = int(parts[1])
    
    column = ord(column) - 96
    
    return row, column