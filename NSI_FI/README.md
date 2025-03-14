# AirX Team Finland contribution

### Description

AirX was developed as an improvement and visualization tool for the 2020-2029 healthy living indicator Burden of Disease by Ambient PM2.5 concentration.
This indicator is currently reported country-wise by the EEA and Eurostat. AirX makes it possible to report the indicator by any NUTS region.

The AirX application requires preprocessed GeoJSON files following a certain "standard". 
To use the app, data needs to be downloaded on the CDSE platform, preprocessed using the provided notebooks, and moved over to the shiny app directory.

We provide some ready-made dummy files.

The app should be hosted by the Shiny Server software, which must be installed first by the user. 
Follow the installation instructions in the dashboard directory and copy the app to the /shiny-server/ directory on your Linux machine.

### Data fetching and preprocessing

The datasets were downloaded mainly from the CDSE platform and the dashboard was hoasted on a Shiny server.

The dashboard and the excess mortality calculations can be replicated following these steps

1. Data Downloads

- Data is downloaded from CAMS databases by running the cdsapi-downloads.ipynb in the Copernicus Data Space Ecosystem's https://dataspace.copernicus.eu/ JupyterLab. The data is turned into a point-data into geojson-file. 

2. Join the data to NUTS3-polygons and calculate the mean values of pollutants inside NUTS3 region. Joining and mean calculations are done running the point_polygon_join.R in R.

3. Excess mortality is estimated by running the estimate-mortality.ipynb file

4. Dashboard takes the geojsons from the earlier steps as source data. Dashboard is made with Shiny and it uses the server and ui -files. There is a separate Readme for setting up the Shiny-server.

