from openpyxl import load_workbook
#from shapely.geometry import mapping, box
#import fiona
from osgeo import ogr, gdal, osr
import numpy

wb = load_workbook('/Users/michael/Desktop/polygon_boxes.xlsx')
sheet=wb.get_sheet_by_name('Sheet1')

data = list(sheet.values)[1:]
boxes = list()

driver = gdal.GetDriverByName('GTiff')


for i,row in enumerate(data):
    pixel_size = 0.1
    raster='/Users/michael/bboxes/tifs/{0}.tif'.format(i)
    coords = row[1:5]
    # If x coordinate is very far west, wrap over dateline
    if coords[0] < -90:
        coords = (coords[2],coords[1],coords[0]+360,coords[3])
    x_min, y_min, x_max, y_max = coords
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    if x_res != 0 and y_res !=0:
        # Make a very big array of 1s
        array=numpy.ones((y_res,x_res))
        print("x_res {0} y_res {1}".format(x_res,y_res))
        print(coords)
        outRaster = driver.Create(raster, x_res, y_res, 1, gdal.GDT_Byte)
    
        outRaster.SetGeoTransform((x_min, pixel_size, 0, y_min, 0, pixel_size))
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()
 
# Below here attempts shapefile related stuff
 
    # bbox=list(box(*coords).exterior.coords)
    # ring = ogr.Geometry(ogr.wkbLinearRing)
    # for point in bbox:
    #     ring.AddPoint(*point)
    # poly = ogr.Geometry(ogr.wkbPolygon)
    # poly.AddGeometry(ring)
    # boxes.append(poly)
    
    
# for bbox in boxes:
#     b = list(bbox.exterior.coords)
#
#
#
# schema = {'geometry':'Polygon', 'properties':{'id':'int','value':'int'}}
#
# for i,bbox in enumerate(boxes):
#     with fiona.open('/Users/michael/bboxes/{0}.shp'.format(i),'w','ESRI Shapefile',schema) as b:
#         b.write({'geometry': mapping(bbox),'properties': {'id':i,'value':1}})
#

