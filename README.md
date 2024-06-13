README

QGIS Layer Color Changer

This Python script provides a set of functions to manage QGIS projects.
It uses the PyQt5 and QGIS libraries to initialize a QGIS application, 
load a project from a PostGIS database, and find a specific layer within a project and change its color and symbology based on rule-based symbology

Dependencies
PyQt5
QGIS
Functions

initialize_qgis(prefix_path=''): This function initializes a QGIS application. The prefix_path argument is optional and defaults to an empty string. If an error occurs during initialization, the function will print the error message and exit the application with a status code of 1.

load_project_from_postgis(uri): This function loads a QGIS project from a PostGIS database. The uri argument should be a string representing the URI of the PostGIS database. If an error occurs while loading the project, the function will print the error message and exit the application with a status code of 1.

find_layer(project, layer_name): This function finds a specific layer within a QGIS project. The project argument should be a QgsProject instance, and layer_name should be a string representing the name of the layer. The function is not yet complete.
