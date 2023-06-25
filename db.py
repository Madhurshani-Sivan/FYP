import pymongo
from pymongo import MongoClient

def get_courselist_collection():
    uri = 'mongodb+srv://fyp:fyp123@courselist.i0n97yv.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(uri)
    db = client.courselist
    collection = db.courselist
    return collection

def get_uni_location_collection():
    uri = 'mongodb+srv://fyp:fyp123@courselist.i0n97yv.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(uri)
    db = client.courselist
    collection = db.uni_location
    return collection
