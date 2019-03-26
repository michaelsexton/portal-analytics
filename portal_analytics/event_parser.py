import json
from shapely.geometry import box
import psycopg2


LAYER_INTERACTION = ["New:LayerInteraction"]
ADD_LAYER = ["Add:CSWRecord", "Add:KnownLayer"]

def create_event_db(rows):
    exceptions = 0
    for row in rows:
        try:
            if row[0] in LAYER_INTERACTION:
                create_layer_interaction_event(row)
            elif row[0] in ADD_LAYER:
                create_add_layer_event(row)
            elif row[0] in ["Add:search", "Advanced Search:", "New:Search"]:
                create_search_event(row)
            elif row[0] in ["ClearMapHandlerClick", "Custom WMS Query", "PermanentLinkHandlerClick", "PrintMapHandlerClick",
                        "ScannedMapsHandlerClick", "New:Help Panel", "New:CustomUI"]:
                create_custom_event(row)
            elif row[0] in ["FileDownloader", "KLWFSDownloader", "NVCL:TSG DOWNLOAD", "New:Downloads"]:
                create_download_event(row)
            elif row[0] in ["Query", "New:Query"]:
                create_query_event(row)
            else:
                print("Unknown event type: " + row[0])
                exceptions += 1
        except Exception as e:
            print("Exception occurred: " + e)
            exceptions += 1
        if exceptions > 10:
            break


def create_layer_interaction_event(row):
    if row[1] == "About":
        return create_custom_event(row)
    elif row[1] == "Add":
        return create_add_layer_event(row)
    elif row[1] == "Remove":
        return create_remove_layer_event(row)





def create_add_layer_event(row):
    LAYER_KEYS = ["layerName", "qualifier", "extent"]

    json_obj = parse_data_structure(row[2])
    if row[0] == "Add:CSWRecord":
        json_obj = parse_data_structure(row[2])
        if row[1].startswith("Layer:"):
            json_obj["layerName"] = row[1].replace("Layer:", "")
        json_obj["qualifier"] = "CSWRecord"
    elif row[0] == "Add:KnownLayer":
        json_obj = parse_data_structure(row[2])
        if row[1].startswith("Layer:"):
            json_obj["layerName"] = row[1].replace("Layer:", "")
        json_obj["qualifier"] = "KnownLayer"
    elif row[0] == "New:LayerInteraction":
        json_obj["qualifier"] = "KnownLayer"
    else:
        print(row)
        raise Exception

    if "bbox" in json_obj:
        json_obj["extent"] = transform_bbox(json_obj["bbox"])

    data = dict()
    for key in json_obj:
        if key in LAYER_KEYS:
            data[key] = json_obj[key]

    if "extent" in data:
        data["extent"] = box(*data["extent"])
        load_sql("add_layers", LAYER_KEYS, data)


def create_search_event(row):
    pass


def create_download_event(row):
    pass


def create_remove_layer_event(row):
    pass


def create_custom_event(row):
    pass


def create_query_event(row):
    pass


def parse_data_structure(data):
    try:
        if data.startswith("Filter:"):
            json_string = data.replace("Filter:", "")
            object = json.loads(json_string)
        else:
            object = json.loads(data)
    except:
        print(data)
        raise Exception
    return object


def transform_bbox(bbox):
    try:
        bbox_obj = json.loads(bbox)
        extent = [float(bbox_obj["westBoundLongitude"]), float(bbox_obj["southBoundLatitude"]),
                  float(bbox_obj["eastBoundLongitude"]),float(bbox_obj["northBoundLatitude"])]
    except:
        print(bbox)
        raise Exception
    return extent


def load_sql(table, keys, data):
    try:
        sql = "insert into {0} (layername, extent, qualifier) values ('{1}', ST_GeomFromText('{2}'), '{3}')".format(table, data["layerName"], data["extent"], data["qualifier"])
        connection = psycopg2.connect("dbname='michael' user='postgres' host='127.0.0.1'")
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
    except:
        print(data)
        raise Exception