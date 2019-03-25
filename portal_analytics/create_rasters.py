import os
import math
from osgeo import gdal, osr
from matplotlib.pyplot import imshow
import numpy as np
import scipy.ndimage as ndi
import json
from . import  parser

PIXEL_SIZE = 0.1

def full(w):
    return w

def log2(w):
    return math.log2(w)

def dec(w):
    return w/10


output_functions = {"output log2":log2}



def create_spatial_data(gdf):
    with open('items.json') as file:
        items = json.load(file)
    layers=  items["layers"]
    for output in output_functions:
        func = output_functions[output]
        if not os.path.exists(output):
            os.makedirs(output)
        for layer in layers:
            layer_path = os.path.join(output,layer)
            if layer == "all":

                if not os.path.exists(layer_path):
                    os.makedirs(layer_path)
                frame=gdf
            else:
                frame = get_data(layers[layer], gdf)
                print(output)
            frame.to_file(layer_path,driver="ESRI Shapefile")
            for row in frame.itertuples():
                shape = getattr(row, "shape")
                weighting = func(getattr(row, "weighting"))
                index = row.Index
                grid, pixel_size = create_grid(shape, weighting)
                if grid.size == 0:
                    continue
                else:
                    create_raster(layer, shape, grid, index, pixel_size, output)

def get_data(layer, gdf):
    print(layer)
    frame = gdf[gdf['ga:eventAction'] == "Layer:"+layer]
    return parser.explode(frame)

def create_grid(shape, weighting, pixel_size = PIXEL_SIZE):

    (x0,y0,x1,y1) = shape.bounds
    width = int((x1-x0)/pixel_size)
    height = int((y1-y0)/pixel_size)
    grid = get_envelope(width, height, weighting)
    print(grid.shape)
    if grid.size == 0:
        grid = get_array(1, 1, weighting)
    return  grid, pixel_size

def create_raster(layer, shape, grid, index, pixel_size, output):

    print(shape.bounds)
    height, width = grid.shape

    x0 = shape.bounds[0]
    y0 = shape.bounds[1]
    print(width,height, pixel_size)

    driver = gdal.GetDriverByName('GTiff')
    filename = "{0}.tif".format(index)
    filepath = os.path.join(output,layer, filename)
    print(filepath)
    outRaster = driver.Create(filepath, width, height, 1, gdal.GDT_Float32)
    outRasterSRS=osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326) # import the EPSG projection
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outRaster.SetGeoTransform((x0, pixel_size, 0, y0, 0, pixel_size))
    outRaster.GetRasterBand(1).WriteArray(grid)
    outRaster.FlushCache()
    del outRaster

def get_envelope (w,h, weighting):
    nparray = get_array(w, h, weighting)
    sig_x, sig_y = get_sigmas(w, h)
    return ndi.filters.gaussian_filter(nparray,sigma=(sig_y,sig_x))

def get_sigmas(w, h):
    return (w / 20, h / 20)

def get_array(width, height, weighting, envelope_factor = 0.6):
    print(weighting)
    env_h = int(height * envelope_factor)
    env_w = int(width * envelope_factor)
    d_h0, d_h1 = get_buffers(height,env_h)
    d_w0, d_w1 = get_buffers(width,env_w)
    envelope = np.ones((env_h, env_w))
    return np.pad(envelope * weighting,((d_h0,d_h1),(d_w0,d_w1)),mode='constant')

def get_buffers(max_l,env_l):
    delta0 = int((max_l-env_l)/2)
    delta1 = max_l - (env_l+delta0)
    return (delta0,delta1)