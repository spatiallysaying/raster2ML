import os
import json
import numpy as np
import ntpath
from collections import OrderedDict

from labelme import utils
import rasterio

class NpEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def make_json_shape(pixels, label):
    """Generate a JSON structure for a given shape."""
    shape = {}
    pixels_list = [list(item) for item in pixels]
    shape["label"] = str(label)
    shape["points"] = pixels_list
    shape["group_id"] = "Airport"
    shape["shape_type"] = "polygon"
    shape["flags"] = {}
    return shape

def generate_labelme_dict(raster_file, df,label_field):
    """Generate a labelme JSON structure using raster and shapefile data."""
    with rasterio.open(raster_file) as src:
        labelme_dict = OrderedDict()
        labelme_dict["version"] = "5.0.4"
        labelme_dict["flags"] = {}
        labelme_dict["shapes"] = []
        
        for _, row in df.iterrows():  # Iterate through each feature
            feature_geom = row['geometry']
            type_name = row[label_field]
            vertices = list(feature_geom.exterior.coords)
            longitudes, latitudes = map(list, zip(*vertices))
            longitudes, latitudes = np.array(longitudes), np.array(latitudes)
            pixels_y, pixels_x = rasterio.transform.rowcol(src.transform, longitudes, latitudes)
            pixels = [(x, y) for y, x in zip(pixels_y, pixels_x)]
            labelme_dict["shapes"].append(make_json_shape(pixels, type_name))

        labelme_dict["imagePath"] = ntpath.basename(raster_file)
        labelme_dict["imageHeight"] = src.height
        labelme_dict["imageWidth"] = src.width
        labelme_dict["imageData"] = None
  
        return labelme_dict

