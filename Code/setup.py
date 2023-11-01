from setuptools import setup, find_packages

This package ... 

setup(
    name='hazards',
    version = '1.0.1'
    author='Joanna Noyes'
    author_email = 'joannanoyes14@gmail.com'
    desciption='A package to plot different aspects of hazard and risk when given a location and river shapefile'
    keywords='hazards, package, Python, risk'
    packages=find_packages()
    install_requires=[
        'numpy >=1.17.3, <1.25.0',
        'matplotlib',
        'pandas',
        'geopandas',
        'plotly',
        'osmnx',
        'shapely',
        'rasterio'
        ],
    )
