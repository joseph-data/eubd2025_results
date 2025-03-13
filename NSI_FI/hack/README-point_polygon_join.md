# Point and polygon join

## General description point and polygon join

This script joins point data to polygons and calculates the mean value of values that are inside a given polygon.

## Input

This script takes two different inputs:

- point data in geojson format containing the different pollutants
- NUTS3 regions from Sweden and Finland

## Prosessing

There are three main processing phases in the point and polygon join
1. Points are joined spatially to NUTS3 regions
2. Geometry is removed from the data frame and then the mean of different pollutants is calculated by the NUTS3 area that they belong
3. Mean values of pollutants are joined to the NUTS3 -regions by NUTS3 region

## Output

Output of this script is a geojson-file that combines the NUTS3-areas and population figures by total, male and female and the mean value of pollutants.








