
from raster2ML import labelme2mask
import argparse
import shutil
import ntpath
import ast
import os.path as osp

'''

$ python labelme2mask.py path/to/your_labelme.json  path/to/output_folder --labels_dict "{'label1': 1, 'label2': 2, ...}"

'''


def main():
    """Main function to convert labelme JSON to labeled image dataset."""
    parser = argparse.ArgumentParser(description="Convert labelme annotated JSON files to masks.")
    parser.add_argument("source_json_file", type=str, help="Annotated LabelMe JSON file")
    parser.add_argument("target_folder", type=str, help="Folder where the masks will be saved.")
    #parser.add_argument("--labels_dict", type=str, help="Dictionary containing label to integer mapping. {'_background_': 0, 'car': 1, 'bike': 2, 'plane': 3, 'boat': 4}" )

    args = parser.parse_args()

    # Load the LabelMe JSON data
    source_json_file=args.source_json_file
    target_folder = args.target_folder
    #labels_dict = ast.literal_eval(args.labels_dict)
    
    
    (data, img) = labelme2mask.get_data_and_image(source_json_file)
    (label_names, lbl) = labelme2mask.get_label_names(data, img)
    mask_file = ntpath.basename(data['imagePath']).split('.')[0]
    mask_file  = mask_file+'_mask'
    print(mask_file)
    labelme2mask.save_image_and_label(img, lbl, args.target_folder, label_names, mask_file)


if __name__ == '__main__':
    main()
