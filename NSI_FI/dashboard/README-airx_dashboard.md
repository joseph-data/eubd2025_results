# The AirX shiny dashboard


## General description of the dashboard

The dashboard is created for the European Big Data Hackathon 2025. The dashboard has two tabs and four main components. 

1. The Map Tab
- The Map Tab allows the user to see the number of excess deaths on a interactive choropleth map by NUTS3 regions
- User can change the output by selecting the total population or the number of excess deaths by sex

2. The Graph and Table Tab
- The  Graph and Table Tab allows the user make comparisons between the two countries (Sweden and Finland) and comparisons between regions
- There is also a table output and the user is also able to use the export-button to export the data to a csv-file to make further analyses outside the dashboard.

The dashboard is comprised of two files:

- ui.R, contains the code for User interface
- server.R, contains the code for all the server-side logic of our application. 

## Input

The dashboard takes following inputs:
Geojsons for the amount of people and pollutants for March 2022 and March 2023
- pohjoismaat_0322-DEATHS.geojson
- pohjoismaat_0323-DEATHS.geojson
 
GeoTiff-files for following gases: Nitrogen dioxide, Methane, Aerosol concentrations 340/380 nm, Carbonmonoxide, Ozon, Sulfur dioxide, Formaldehyde
- NO2.tiff
- CH4.tiff
- AER_AI_340_380.tiff
- CO.tiff
- O3.tiff
- SO2.tiff
- HCHO.tiff

For the visualisation purposes we also have added the Corine landuse layear from via wms and as a base map we use the Open street map -tiles.

## Prosessing

The dataset is pivoted to a long format to enable the visualisations.

## Output

Outputs of this application are: 
- The two different tabs with their map and graph and table functions and the csv-file that the user is able to generate by a press of a button.






