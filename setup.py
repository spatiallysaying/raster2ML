from setuptools import setup, find_packages

setup(
    name="raster2ML",
    version="0.1.0",
    description="Convert georeferenced Geotiff or any spatial raster format to machine learning ready data.",
    author="Durga Prasad, Dhulipudi",
    author_email="dgplinux@yahoo.com",
    url="https://github.com/spatiallysaying/raster2ML",
    packages=find_packages(),
    install_requires=[
        'geopandas',
        'rasterio',
        'gdal',
        'labelme',
        # add other dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
