from cellartracker import cellartracker
from getpass import getpass
password = getpass('Password: ')

username = 'knut.a.kvale@gmail.com'


client = cellartracker.CellarTracker(username, password)

client.get_list()           # Return List
client.get_inventory()      # Return Inventory

inventory = client.get_inventory()
lst = client.get_list()

