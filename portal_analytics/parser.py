import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import box, Point
import shapely.ops as ops
import pyproj
from functools import partial
from json import JSONDecodeError

# TODO refactor this

SHAPE_FIELD='shape'

def create_dataframe(rows, headers):
  df = pd.DataFrame(rows, columns=headers)
  return df


def process_dataframe(dataframe, shape=SHAPE_FIELD):
  if type(dataframe) == dict:
    dataframe = create_dataframe(dataframe)
  dataframe['parsed'] = dataframe["ga:eventLabel"].apply(label_filterer)
  dataframe["shape"] = dataframe['parsed'].apply(parse_geometry)
  #new_frame = dataframe['parsed'].apply(pd.Series)
  #parsed_json = pd.concat([dataframe[:],new_frame[:]], axis=1)
  #parsed_json[shape] = parsed_json['bbox'].apply(parse_bbox)
  return dataframe
  

def create_geodataframe(dataframe, geometry=SHAPE_FIELD):
  if type(dataframe) == dict:
    dataframe = create_dataframe(dataframe)
  geom_mask = dataframe[geometry].notnull()
  return gpd.GeoDataFrame(dataframe[geom_mask], geometry=geometry)

def explode(dataframe):
  new_frame =  pd.concat([dataframe, dataframe["parsed"].apply(pd.Series)], axis=1)
  for col in new_frame.columns:
      new_frame[col] = new_frame[col].apply(join_list)
  return new_frame[new_frame[SHAPE_FIELD].notnull()]

def join_list(a):
    if type(a) == list:
        return ', '.join([str(item) for item in a])
    else:
        return a

def label_filterer(data):
  try:
    if data.startswith("Filter:"):
      string = data.replace("Filter:","")
      return json_parser(string)
    elif data.startswith("parameters:"):
      string = data.replace("parameters:","")
      return json_parser(string)
    elif data.startswith("Search parameters:"):
      string = data.replace("Search parameters:","")
      return json_parser(string)
  except ParserException:
    return dict()

def parse_geometry(label):
  try:
  
    bbox_json = label['bbox']
    return parse_bbox(bbox_json)
  except (KeyError, TypeError):
    return None
    
def parse_bbox(json):
  try:
    bbox = json_parser(json)
    if type(bbox) == dict:
      if bbox['westBoundLongitude'] > bbox['eastBoundLongitude']:
        bbox['eastBoundLongitude'] = float(bbox['eastBoundLongitude']) + 360
      if bbox['westBoundLongitude'] == bbox['eastBoundLongitude']:
        bbox['westBoundLongitude'] = float(bbox['westBoundLongitude']) - 0.01
        bbox['eastBoundLongitude'] = float(bbox['eastBoundLongitude']) + 0.01
      if bbox['northBoundLatitude'] == bbox['southBoundLatitude']:
        bbox['northBoundLatitude'] = float(bbox['northBoundLatitude']) + 0.01
        bbox['southBoundLatitude'] = float(bbox['southBoundLatitude']) - 0.01
      return box(*map(lambda x: float(x),(bbox['westBoundLongitude'],bbox['northBoundLatitude'],bbox['eastBoundLongitude'],bbox['southBoundLatitude'])))
    else:
      return None
  except ParserException:
      return None


def json_parser(json_string):
  try: 
    parsed = json.loads(json_string)
  except (JSONDecodeError, TypeError):
    raise ParserException
  if type(parsed) != dict:
    raise ParserException
  return parsed
  
class ParserException(Exception):
  pass