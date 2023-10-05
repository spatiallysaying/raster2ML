'''
Defines a set of functions that transform a given labelme JSON file into a labeled image (mask).
'''

import argparse
import base64
import json
import os
import os.path as osp
import ast
from labelme import utils
import glob
from tqdm import tqdm
import ntpath
import shutil


def str2dict(dict_str):
    """Convert a string representation of a dictionary into an actual dictionary."""
    try:
        return ast.literal_eval(dict_str)
    except:
        raise ValueError(f"Invalid dictionary string: {dict_str}")

def get_data_and_image(json_file):
    """Retrieve image data from JSON or its associated file."""
    with open(json_file, 'rb') as json_f:
        data = json.load(json_f)
        image_data = data.get('imageData')
        if not image_data:
            image_path = os.path.join(os.path.dirname(json_file), data['imagePath'])
            with open(image_path, 'rb') as image_f:
                image_data = image_f.read()
                image_data = base64.b64encode(image_data).decode('utf-8')
        img = utils.img_b64_to_arr(image_data)
        return data, img

def get_label_name_dict(data):
  # Extracting unique 'label' values
  unique_labels = list(set(shape["label"] for shape in data["shapes"]))

  # Creating a dictionary mapping with '_background_' set to 0
  label_dict = {'_background_': 0}
  for idx, label in enumerate(unique_labels, start=1):
      label_dict[label] = idx

  # Printing the dictionary
  return label_dict


'''
The function get_label_names(data, image) retrieves the set of label names and their associated values. 
It also maps shapes from the JSON to the image to create a label mask. The label_name_to_value dictionary 
can be externalized as an argument or configuration for better flexibility.
'''
def get_label_names(data, image):

    label_name_to_value=get_label_name_dict(data)
    """Extract label names from data and map shapes to labels."""
    for shape in sorted(data['shapes'], key=lambda x: x['label']):
        label_name = shape['label']
        if label_name not in label_name_to_value:
            label_value = len(label_name_to_value)
            label_name_to_value[label_name] = label_value
			
    lbl, _ = utils.shapes_to_label(image.shape, data['shapes'], label_name_to_value)
    label_names = [None] * (max(label_name_to_value.values()) + 1)
    for name, value in label_name_to_value.items():
        label_names[value] = name
    return label_names, lbl

def save_image_and_label(image, lbl, output_dir, label_names, mask_file):
    """Save the labeled image (mask) to the specified output directory."""
    utils.lblsave(osp.join(output_dir, mask_file), lbl)
    print('Maks generated at ',osp.join(output_dir, mask_file))
