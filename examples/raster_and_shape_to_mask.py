from raster2ML import labelme2mask,raster2png,shp2labelme

import os
import argparse
import json
import shutil
import ntpath
import ast
import os.path as osp

os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import rasterio

'''
Purpose : Given a Raster file and corresponding shapefile, raster mask file is created with class names per the specified shapefile field.
Output :  An 8bit png file, where each class is represented in different color
Usage 

python raster2png_and_mask.py "C:/Images/raster_image.tif" "C:/Shapefiles/footprint_shapefile.shp" "label_field_name" "C:/Masks_folder/"

These three activities are carried out in that order
raster2png
shp2labelme
labelme2mask

'''
def main():
    parser = argparse.ArgumentParser(description="Generate labelme JSON from ESRI Shapefile and Rasters.Converts labelme JSON to Raster Mask")
    parser.add_argument('raster_file', help='Path to the raster image')
    parser.add_argument('shapefile_path', help='Path to the ESRI Shapefile.')
    parser.add_argument('label_field', help='Field name in the Shapefile that has label names(class names)')
    parser.add_argument("target_folder", type=str, help="Folder where the masks will be saved.")

    args = parser.parse_args()

    raster_file = args.raster_file    
    shapefile_path=args.shapefile_path
    label_field=args.label_field
    target_folder = args.target_folder

    if not osp.exists(target_folder):
      os.makedirs(target_folder)

        
    # Load the shapefile data
    gdf = gpd.read_file(shapefile_path)

    # Check CRS of raster and shapefile
    with rasterio.open(args.raster_file) as raster_ds:
        raster_crs = raster_ds.crs.to_epsg()
        print('Raster parsed ',raster_crs)
    shapefile_crs = gdf.crs.to_epsg()

    if raster_crs != shapefile_crs:
        print(f"Error: The raster and the shapefile are not in the same coordinate system. Raster CRS: {raster_crs}, Shapefile CRS: {shapefile_crs}")
        gdf=None
        return
    
    png_file=raster2png.scale_to_8bit(raster_file, target_folder) #Generate PNG file in 8 bit    
    #ext=ntpath.basename(raster_file).split('.')[1]
    #png_file=raster_file.replace(ext, 'png')  #Use the PNG file in 8 bit as source to LabelMe
    
    #Create LabelMe JSON File        
    json_dict = shp2labelme.generate_labelme_dict(png_file, gdf,label_field)    
   
    source_json_file=png_file.replace('.png', '.json')
    with open(source_json_file, 'w') as f:
        json.dump(json_dict, f, indent=4, cls=shp2labelme.NpEncoder)

    print('LabelMe JSON generated at ',source_json_file)
    
    #Each label will be in a different color
    # Get unique values from the desired field
    unique_values = gdf[label_field].unique()
    label_dict = {'_background_': 0}
    for idx, value in enumerate(unique_values, start=1):
        label_dict[value] = idx

    gdf=None

    #Create PNG Mask File
    (data, img) = labelme2mask.get_data_and_image(source_json_file)
    (label_names, lbl) = labelme2mask.get_label_names(data, img)
    mask_file = ntpath.basename(data['imagePath']).split('.')[0]
    mask_file  = mask_file+'_mask'
    labelme2mask.save_image_and_label(img, lbl, args.target_folder, label_names, mask_file)


if __name__ == '__main__':
    main()
