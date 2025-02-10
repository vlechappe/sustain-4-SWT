# Technico-environmental model source code

This repository contains all the source code used for the technico-environmental analysis presented in our article.

## Requirements

* Brightway2
* AB environment
* Ecoinvent 3.8
* Python 3
* Jupyter notebook

## Informations about the code

To use this code, you have to create a project in Activity Browser. You can use the default name "ACV_eol". Then you have to dowload a few databases.The default databases are ecoinvent 3.8 cutoff and biosphere3. You can download ecovinvent 3.8 cutoff directecly from Activity Browser or from the website EcoInvent. In both case, make sure that the two databases are named : "ecoinvent-3.8-cutoff" and "biosphere3". Then, you can import the databases from the file "bw2_DB" and link them to ecoinvent-3.8-cutoff. Just be sure to import "oswacc.bw2package" before "electronics_wind_turbine_oswacc.bw2package". In general, make sure that the names of the databases in your Activity Browser project and in the code are the same.
