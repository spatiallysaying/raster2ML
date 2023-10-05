from raster2ML import raster2png

import os
import argparse
import ntpath

'''
Usage 

python test_raster2png.py "C:/input_folder/raster_image.tif" "C:/out_folder/raster_image.png"

'''
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert GeoTiff to PNG.")
    parser.add_argument('src_raster', type=str, help="Path to source GeoTiff.")
    parser.add_argument('output_folder', type=str, help="Path to output folder.")
    args = parser.parse_args()
    
    if not os.path.exists(args.output_folder):
      os.makedirs(args.output_folder)

    raster2png.scale_to_8bit(args.src_raster, args.output_folder)

    