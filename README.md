Certainly! Here's an updated `README.md` content based on your new descriptions:

---

# raster2ML

## Purpose

`raster2ML` is a utility designed to process a Raster file and its corresponding shapefile to produce a raster mask file. The mask assigns class names based on the specified field in the shapefile.

## Output

The result is an 8-bit PNG file where each distinct class from the shapefile is represented by a different color.

## Processes

### 1. raster2png

- **Description**: Converts a Raster image into an 8-bit PNG.
- **Usage**: _Specific usage instructions for this function, if separate from the main command._

### 2. shp2labelme

- **Description**: Generate a `labelme` JSON structure using raster and shapefile data.
- **Usage**: _Specific usage instructions for this function, if separate from the main command._

### 3. labelme2mask

- **Description**: Defines a set of functions that transform a given `labelme` JSON file into a labeled image (mask).
- **Usage**: _Specific usage instructions for this function, if separate from the main command._

## Main Usage

To utilize the combined functionality of the library, run:

```
python raster2png_and_mask.py "C:/Images/raster_image.tif" "C:/Shapefiles/footprint_shapefile.shp" "label_field_name" "C:/Masks_folder/"
```

## Dependencies

Ensure you have all the necessary dependencies installed. Refer to `requirements.txt` for a list of required packages.

---
