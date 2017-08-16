import arcpy
arcpy.env.workspace="e:/tifs"
tifs = arcpy.ListDatasets("*", "Raster")
arcpy.MosaicToNewRaster_management(tifs,"E:/","output.tif",None, None,None,1,"SUM")