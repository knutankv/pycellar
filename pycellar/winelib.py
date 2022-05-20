from cellartracker import cellartracker
from getpass import getpass
import re
import pandas as pd
import numpy as np
from datetime import date
from functools import total_ordering

standard_keys = ['iwine', 'vintage', 'producer', 'appellation', 'region', 'varietal', 'bin', 
                 'size', 'wine', 'type']

class Cellar:
    def __init__(self, wines):
        self.wines = wines
        self.wines.sort()
        self.wines_filt = wines*1
    
    def to_df(self, use_filtered=True, keys=None, unique=True):     
        if use_filtered:
            wines = self.wines_filt
        else:
            wines = self.wines
            
        if keys is None:
            keys = standard_keys*1
        
        all_wines = [wine.to_series(keys=keys) for wine in wines]
        
        if len(all_wines)>0:
            df = pd.concat(all_wines, axis=1).transpose()
            df = df.set_index('iwine')
            
            if unique:
                iwine_unique, ixs, counts = np.unique(df.index, return_counts=True, return_index=True)
                df = df.iloc[ixs]
                df['bottles'] = counts
        else:
            df = pd.DataFrame(columns=keys)
            if unique:
                df['bottles'] = []

        return df
    
    @property
    def unique_filt_wines(self):
        wines = self.wines_filt
        unique_wines = []
        for wine in wines:
            if wine not in unique_wines:
                unique_wines.append(wine)
        
        return unique_wines
    
    @property
    def unique_wines(self):
        wines = self.wine
        unique_wines = []
        for wine in wines:
            if wine not in unique_wines:
                unique_wines.append(wine)
        
        return unique_wines

    def get_wine_dict(self):
        return {wine.barcode: wine.full_name for wine in self.wines}
    
    def get_dash_dict(self, unique=True):
        barcodes = [wine.barcode for wine in self.wines]
        labels = [wine.full_name for wine in self.wines]
        
        if unique:
            __, ixs, counts = np.unique(labels, return_counts=True, return_index=True)
            labels_unique = [None]*len(ixs)
            barcodes_unique = [barcodes[ix] for ix in ixs]
            
            for i,ix in enumerate(ixs):
                if counts[i]>1:
                    count_label = f': {counts[i]} flasker'
                else:
                    count_label = ''
                
                labels_unique[i] = f'{labels[ix]}{count_label}'

            labels = labels_unique*1
            barcodes = barcodes_unique*1
        
        return [{'label': label, 
                 'value': barcode} for barcode, label in zip(barcodes, labels)] 
    
    def get_props(self, key):
        return [getattr(wine, key) for wine in self.wines]
    
    def filter_wines(self, fun):
        wines = []
        for wine in self.wines:
            if fun(wine):
                wines.append(wine)
                
        self.wines_filt = wines
        self.wines_filt.sort()
        

    def get_consumable_wines(self, year=None):
        year = year or date.today().year
        fun = lambda wine: wine.is_consumable(year)
        
        return self.filter_wines(fun)
        

    def rfilter_wines(self, key, r, if_invalid_return=True):
        def fun(wine):
            try:
                return np.min(r)<=np.float(getattr(wine, key))<=np.max(r)
            except:
                return if_invalid_return
  
        return self.filter_wines(fun)
    
    def eqfilter_wines(self, key, val):
        fun = lambda wine: getattr(wine, key) == val 
        return self.filter_wines(fun)
    

    def wines_from_barcode(self, barcode, unique=False):
        barcodes = [wine.barcode for wine in self.wines]
        
        ix = [i for i, x in enumerate(barcodes) if x == barcode]
        wines = [self.wines[this_ix] for this_ix in ix]
        
        if len(wines) == 0:
            wines = None
        elif unique:
            wines = wines[0]
            
        return wines
        
    def wines_from_barcodes(self, barcodes):
        all_wines = [self.wines_from_barcode(bc) for bc in barcodes]
        all_wines_flattened = [i for j in all_wines for i in j]
        return all_wines_flattened
        
    @classmethod
    def from_cellartracker_inventory(cls, username, password=None):
        inventory = get_cellartracker_inventory(username, password=password)
        
        wines = []
        
        for wine_dict in inventory:
            wines.append(Wine(wine_dict))


        return cls(wines)


class Wine:
    def __init__(self, wine_dict):
        for key in wine_dict:
            setattr(self, str(key).lower(), wine_dict[key])
        
        self.barcode = int(self.barcode)
        self.iwine = int(self.iwine)
    
  
    @total_ordering
    def __lt__(self, other):
        return self.iwine<other.iwine
  
    def __eq__(self, other):
        return self.iwine == other.iwine
  
    def __le__(self, other):
        return self.iwine<= other.iwine
      
    def __ge__(self, other):
        return self.iwine>= other.iwine
          
    def __ne__(self, other):
        return self.iwine != other.iwine
    
    
    @property
    def full_name(self):
        return f'{self.vintage} {self.producer} {self.appellation} ({self.region} {self.varietal})'

    @property
    def med_name(self):
        return f'{self.vintage} {self.producer} {self.appellation}'
    
    
    def __repr__(self):
        return self.full_name
    
    def to_series(self, keys=None):
        if keys is None:
            keys = standard_keys*1
            
        series = pd.Series(dtype='object')
        
        for key in keys:
            series[key] = getattr(self, key)
            
        return series
    
    def is_consumable(self, year=None):
        year = year or date.today().year
        
        max_year = self.endconsume
        min_year = self.beginconsume
        
        if max_year == '':
            max_year = np.inf
        if min_year == '':
            min_year = -np.inf
            
        
        return float(min_year) < year < float(max_year)
    
    def in_range(self, key, r, if_invalid_return=True):
        try:
            return np.min(r)<=np.float(getattr(self, key))<=np.max(r)
        except:
            return if_invalid_return
        

def get_cellartracker_inventory(username, password=None):
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

username = 'knut.a.kvale@gmail.com'
password = 'minvin'

test = get_cellartracker_inventory(username, password=password)