
from  raster2ML import shp2labelme

import os
import argparse
import json
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import rasterio
import ntpath

'''
Usage 

python shp2labelme.py path/to/your_shapefile.shp  path/to/raster_file.tif <label_field>

'''
def main():
    parser = argparse.ArgumentParser(description="Generate labelme JSON from ESRI Shapefile and Rasters.")
    parser.add_argument('raster_file', help='Path to the raster image')
    parser.add_argument('shapefile_path', help='Path to the ESRI Shapefile.')
    parser.add_argument('label_field', help='Field name in the Shapefile that has label names(class names)')

    args = parser.parse_args()

    print('Arguments parsed')
    # Load the shapefile data
    shapefile_path=args.shapefile_path
    gdf = gpd.read_file(shapefile_path)
    raster_file = args.raster_file
    
   
    label_field=args.label_field    
    
    # Check CRS of raster and shapefile
    with rasterio.open(args.raster_file) as raster_ds:
        raster_crs = raster_ds.crs.to_epsg()
        print('Raster parsed ',raster_crs)
    shapefile_crs = gdf.crs.to_epsg()

    print('Comparing CRS')
    if raster_crs != shapefile_crs:
        print(f"Error: The raster and the shapefile are not in the same coordinate system. Raster CRS: {raster_crs}, Shapefile CRS: {shapefile_crs}")
        return    

    file_json = shp2labelme.generate_labelme_dict(raster_file, gdf,label_field)
    
    ext=ntpath.basename(raster_file).split('.')[1]

    with open(raster_file.replace(ext, 'json'), 'w') as f:
        json.dump(file_json, f, indent=4, cls=shp2labelme.NpEncoder)

    print('Label Me JSON generated at ',raster_file.replace(ext, 'json'))
    gdf=None

if __name__ == '__main__':
    main()
