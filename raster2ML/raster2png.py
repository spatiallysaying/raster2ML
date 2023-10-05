
'''

This solution offers a methodological approach to rescaling raster data in a way that enhances visual contrast.By offering multiple options for determining the stretch 
(percentile, mean/std deviation), it provides a versatile tool for different kinds of images. The results of this method can indeed produce clearer and more visually 
appealing 8-bit images from 16-bit sources. It's a  contribution to the conversation on image processing and enhancement using GDAL in Python!


Converts a Raster image into a 8bit PNG 
The method is adapted from QGIS plugin 'LF Tools' 
QGIS LF Tools Plugin-->https://github.com/LEOXINGU/lftools#rescale-to-8-bit
github -->https://github.com/LEOXINGU/lftools/blob/main/processing_provider/Rast_rescaleTo8bits.py

Focus is on enhancing the contrast using the 2nd and 98th percentiles of the data, a technique sometimes referred to as "contrast stretching" or "percentile stretching".
By doing this, we are`tially discarding the darkest 2% and brightest 2% of the pixel values, which often helps 
in highlighting features in the main body of the data.

Here are some key takeaways from this solution:

Quantile-Based Stretching: By using the 2nd and 98th percentiles (np.quantile(band,0.02) and np.quantile(band,0.98)), we are focusing on the core range of the data, which can 
often help in removing noise or extreme outliers that can affect the visual representation of the image.

Scaling Calculation: After determining the min and max values (whether they're derived from direct min/max, percentiles, or mean and standard deviation),we are scaling the pixel
values linearly to fit the 8-bit range (0-255).

Null Pixel Handling: This solution also incorporates handling for NoData or null pixels. This is essential as these pixels should not influence the stretching or scaling 
computations.

By Band Processing: We arealso providing the option to either process each band individually or use the overall min/max across all bands for scaling.This offers flexibility 
depending on the nature and requirements of the imagery we are working with.

'''


import os
import numpy as np
import shutil
import ntpath
import uuid

from osgeo import gdal, osr
import rasterio


def delete_raster_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"File {filepath} deleted successfully!")
    else:
        print(f"File {filepath} does not exist!")

def Geotiff2PNG(src_name,dst_name):  
    with rasterio.open(src_name) as src:  
        kwargs = src.meta.copy()  
        kwargs.update({  
            "driver": "PNG",  
            'dtype': 'uint8',
            'transform': src.transform,  
            'width': src.width,  
            'height': src.height  
        })  
  
        with rasterio.open(dst_name, 'w', **kwargs) as dst:  
            for i in range(1, src.count + 1):  
                dst.write(src.read(i), i)    
                
'''
1)Scale raster to 8 bit , avoid loss of quality by use of quantile teqchnique
2)Save intermediate Geotiff in 8 bit
3)Use rasterio to convert 8 bit Geotiff to PNG 

'''                
                
def scale_to_8bit(INPUT_RASTER, OUTPUT_FOLDER):

    print('Opening raster...',INPUT_RASTER)
    image = gdal.Open(INPUT_RASTER)
    prj = image.GetProjection()
    geotransform  = image.GetGeoTransform()
    GDT = image.GetRasterBand(1).DataType
    NO_DATA_VAL = image.GetRasterBand(1).GetNoDataValue()
    n_bands = image.RasterCount
    cols = image.RasterXSize
    rows = image.RasterYSize
    CRS = osr.SpatialReference(wkt=prj)
    

    TEMP_RASTER = os.path.join(OUTPUT_FOLDER, f'temp_file_{uuid.uuid4()}.tif')
    fname,_ = ntpath.basename(INPUT_RASTER).split('.')        
    OUTPUT_RASTER= os.path.join(OUTPUT_FOLDER,fname+'_8bit.png')
    
    print(TEMP_RASTER)
    print(OUTPUT_RASTER)

    # Constants
    BYBAND=True
    TYPE=1
    nullPixel=False

    if n_bands==1: #For ML Dataset RGB is sufficient 
        print('It is Gray scale image...aborting conversion')
        image = None # Close dataset
        return
    if n_bands==4:  #For ML Dataset RGB is sufficient 
        n_bands=3
   
    if GDT==3: #If already 8bit image, then no need to process
        image = None # Close dataset

        Geotiff2PNG(INPUT_RASTER,OUTPUT_RASTER)
        return
            
    # Create driver
    Driver = gdal.GetDriverByName('GTiff').Create(TEMP_RASTER, cols, rows, n_bands, gdal.GDT_Byte)
    Driver.SetGeoTransform(geotransform)
    Driver.SetProjection(CRS.ExportToWkt())

    print('Calculating statistics...')
    bands = []
    max_values,min_values = [],[]
    for k in range(n_bands):
        band = image.GetRasterBand(k+1).ReadAsArray()
        bands += [band]
        # Remove null pixels of the statistics
        if NO_DATA_VAL:
            band = band[band != NO_DATA_VAL]
        # Max e Min
        if TYPE == 0:
            max_values += [band.max()]
            min_values += [band.min()]
        # Quantile (2% - 98%)
        if TYPE == 1:
            max_values += [np.quantile(band,0.98)]
            min_values += [np.quantile(band,0.02)]
        # Media ± 2*DesvPad
        if TYPE == 2:
            max_values += [band.mean() + 2*band.std()]
            min_values += [band.mean() - 2*band.std()]
            
        band= None
        
    if not BYBAND:
        Max = np.max(max_values)
        Min = np.min(min_values)

    # Rescale and save bands
    print('Rescaling and saving bands...')
    for k in range(n_bands):
        band = bands[k]
        if BYBAND:
            Max = max_values [k]
            Min = min_values[k]
        if nullPixel:
            transf = (255*(band.astype('float')- Min)/(Max-Min) + 0.5).round()
        else:
            transf = (256*(band.astype('float')- Min)/(Max-Min) - 0.5).round()
        if TYPE in [1,2]:
            transf = ((transf>0)*(transf<=255))*transf + 255*(transf>255)
            if nullPixel:
                transf = transf*(band != NO_DATA_VAL)

        transf = transf.astype('uint8')
        outband = Driver.GetRasterBand(k+1)
        print('Writing Band {}...'.format(k+1))
        outband.WriteArray(transf)
        if nullPixel:
            outband.SetNoDataValue(0)

    image = None # Close dataset
    Driver.FlushCache() # write to disk
    Driver = None  # save, close
    print('Completed writing to intermediate ...',TEMP_RASTER)
    
    Geotiff2PNG(TEMP_RASTER, OUTPUT_RASTER)    
    print('Completed writing to ...',OUTPUT_RASTER)
    

    delete_raster_file(TEMP_RASTER)        
    print('Deleting intermediate file  ...',TEMP_RASTER)
    
    print('Operation completed successfully!')
    
    return OUTPUT_RASTER
