import gdal
import json
from . import  parser

def create_spatial_data(gdf):
  with open('items.json') as file:
      items = json.load(file)
  layers=  items["layers"]
  for layer in layers:
    frame = get_data(layers[layer], gdf)
    print(frame)
    frame.to_file("output/"+layer,driver="ESRI Shapefile")
    
  
  

def get_data(layer, gdf):
  print(layer)
  frame = gdf[gdf['ga:eventAction'] == "Layer:"+layer]
  return parser.explode(frame)
 
#def create_raster:
#  target_ds = gdal.GetDriverByName('GTiff').Create(output, x_res, y_res, 1, gdal.GDT_Byte)
