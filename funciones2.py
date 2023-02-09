from dateutil import parser
import pandas as pd
from datetime import datetime
from pymongo import *

from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

def groupByDayAndShift(df):

    df = df.groupby(['fecha','weekday','shift']).size().reset_index(name='count')
    
    return df




    
def getOrdersV4(start_date, end_date, shop, city):
    
    ''' retorna un DataFrame con las ordenes '''
    iso = parser.parse(start_date)
    iso2 = parser.parse(end_date)
    td = pd.Timedelta(3, "h")
    iso_corregido = iso+td
    iso2_corregido=iso2+td
         
    uri=('mongodb://user@xx.xx.xxx.191:x/db')
     
    client = MongoClient(uri)

    mydatabase = client.deliveratedb
    mydatabase.list_collection_names()

    if (shop=='todos' and city=='todos'):
        collection = mydatabase["orders"].find({ '$and': [{'created_date': { '$gt':(iso_corregido),'$lt':(iso2_corregido)}                               
                                     }]},{'created_date':1,'shift':1,'city':1, 'consumer_canceled_date':1})

    elif shop == 'todos': 
        collection = mydatabase["orders"].find({ '$and': [{'created_date': { '$gt':(iso_corregido),'$lt':(iso2_corregido)}, 'city' : city                                
                                     }]},{'created_date':1,'shift':1,'city':1, 'consumer_canceled_date':1})

    elif city == 'todos': 
        collection = mydatabase["orders"].find({ '$and': [{'created_date': { '$gt':(iso_corregido),'$lt':(iso2_corregido)}, 'shop_name' : shop                                
                                     }]},{'created_date':1,'shift':1,'city':1, 'consumer_canceled_date':1})

    else:
        collection = mydatabase["orders"].find({ '$and': [{'created_date': { '$gt':(iso_corregido),'$lt':(iso2_corregido)}, 'shop_name' : shop , 'city':city                             
                                     }]},{'created_date':1,'shift':1,'city':1, 'consumer_canceled_date':1})

    list_col = list(collection)
    df=pd.DataFrame(list_col)
    return df                                 


def deleteCanceled(df):
    try:
        df=df[df.consumer_canceled_date.isnull()]
    except AttributeError:
        return df    
    
    return df

def getShops():
    
    ''' retorna un dataframe con los clientes'''
  
    uri=('mongodb://user@xx.xx.xxx.191:x/db')
    client = MongoClient(uri)
    start_date = '2022-08-13'
    iso = parser.parse(start_date)
    mydatabase = client.deliveratedb
    mydatabase.list_collection_names()
    #collection = mydatabase["orders"].dinstinct('shop_name' ,{'created_date': { '$gte':iso}})
    collection = mydatabase["orders"].find({'created_date': { '$gte':iso}                             
                                     }).distinct('shop_name')
    list_col = list(collection)
    df=pd.DataFrame(list_col)
    return df

def corregirCreatedDate(df):
    td = pd.Timedelta(-3, "h")
    df["created_date"]=df["created_date"]+td
    return df

