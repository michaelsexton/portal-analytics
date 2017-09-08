import arcpy
import os
WORKSPACE = r"I:\geoscience portal\google analytics\2017-08\outputs v2\all"
dirs = [dir for dir in os.listdir(WORKSPACE) if not dir.startswith('.')]
for dir in dirs:
    arcpy.env.workspace=os.path.join(WORKSPACE,dir)
    tifs = arcpy.ListDatasets("*.tif", "Raster")
    output_filename = "{0}.tif".format(dir)
    arcpy.MosaicToNewRaster_management(tifs,WORKSPACE,output_filename,None,  "32_BIT_FLOAT",None,1,"SUM")