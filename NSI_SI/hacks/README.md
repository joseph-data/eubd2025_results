## **Tools and Model Architecture**

Here, you can find the tools and model architecture methods used for our prototype.  
The tools are focused on **preparing Analysis-Ready Data (ARD) Sentinel-2 cloudless composites from 2017** to create a deep learning dataset.

**This is a prototype made in a few days on liters of coffee and sandwiches**, and of course, it can be **tremendously improved** by **merging or/and skipping steps** and incorporating **monthly time series analysis (within year) and many other advanced things that Homo Sapiens can when they have time - and will do :)**.
The dashboard in this repository is a **demonstration of how statistical insights can be visualized** using the extracted tabular data. Future improvements could include integrating additional EO datasets, refining the classification model, adding more statistical indicators, awesome things (just imagine awesome things) and improving data visualization techniques.

The code is designed to process data on **Creodias**, enabling efficient retrieval and transformation of Sentinel-2 imagery for deep learning applications.

## Setting Up the Environment

Before running the scripts in this repository, you need to configure the necessary environment credentials. These credentials allow access to remote EO data storage and optimize performance settings:

```sh
export AWS_S3_ENDPOINT=<your_s3_endpoint>
export AWS_ACCESS_KEY_ID=<your_access_key>
export AWS_SECRET_ACCESS_KEY=<your_secret_key>
export AWS_HTTPS=YES
export AWS_VIRTUAL_HOSTING=FALSE
export GDAL_HTTP_TCP_KEEPALIVE=YES
```

Replace `<your_s3_endpoint>`, `<your_access_key>`, and `<your_secret_key>` with your actual credentials. This setup is required for accessing Sentinel-2 data via Creodias.

## Overview of the Dashboard and Data Processing Pipeline

This repository contains code for a Shiny dashboard that demonstrates how to plot statistical graphs from tabular data. The tabular data used in this dashboard is the result of an analysis pipeline applied to Earth Observation (EO) data. The process moves through multiple stages, from retrieval to transformation, analysis-ready data preparation, and classification using deep learning.

## Major Processing Steps and Scripts

### 1. **Retrieving Sentinel-2 Data**
- **`s2_fetch.py`**: This script streams Sentinel-2 bands of choice directly from Creodias. It connects to the S3 bucket and retrieves all cloud-free images based on user-defined parameters. The data is then transformed to a harmonized CRS (EPSG:3035). We retrieve just bands 12, 11 and 4, to use them for classifcation of impervious with CNN.
Logic:
-- Load processed tiles
-- Load cached features or query STAC
-- Select largest scenes per tile (we are assuming that the largest have all the area covered, not pizza slices in the corner)
-- Process each band in parallel

### 2. **Filtering Minimal Common Tile for Time Series**
- **`min_common_tiles.py`**: After retrieving Sentinel-2 data, this script determines the minimal common tile in the selected areas, ensuring that only tiles available across all years (2017-2023) are used for prototyping time series analysis.

### 3. **Creating Virtual Rasters of bands aggreted per year**
- **`s2bands_to_yearly_vrt.py`**: Since pixel alignments are not exact after CRS transformation, this script creates virtual rasters with a common extent. It ensures spatial consistency across datasets before further analysis.

### 4. **Handling Virtual Rasters and Extent Alignment**
- **`vrt_extent_check.py`**: With this you can check if the script above did it well. After that we are going to a H5 matrix world and this is the last step to check if our data is 1:1.

### 5. **Clipping and Transforming Land Cover Data**
- **`clip_and_resample_s2glc.py`**: This script clips Sentinel-2 land cover data to the areas of interest and resamples it from 10 to 20 m with a simple mode (labels are categories)
- The Sentinel-2 Land Cover dataset (`S2GLC_Europe_2017_clipped_20m`) was transformed and reclassified based on a new categorization scheme using GRASS GIS (`r.reclass`):

| Original Class | Reclassified Category |
|---------------|----------------------|
| Artificial surfaces and constructions | Impervious land |
| Cultivated | Green space |
| Vineyards | Green space |
| Herbaceous | Green space |
| Deciduous | Green space |
| Coniferous | Green space |
| Moors and Heathland | Green space |
| Sclerophyllous vegetation | Green space |
| Natural material surfaces | Impervious land |
| Permanent snow, glaciers | Other |
| Marshes | Other |
| Peatbogs | Other |
| Water bodies | Other |

### 6. **Creating and Checking Analysis-Ready Data (ARD) in HDF5 Format**
- **`gdal2h5.py`**:
- Loads VRT files from a directory, containing Sentinel-2 band data.
- Loads a label file (clipped classification data).
- Generates HDF5 datasets for Sentinel-2 bands and labels.
- Uses chunked reading (256x256 tiles) to process large files efficiently.
- Replaces zero values with NaN in band data to handle missing values.
- Uses gzip compression for efficient storage.
- Processes and stores data in an HDF5 file for use in ML or GIS applications.


### 7. **Code to check the integrity of theHDF5**
- **`check_h5.py`**



### 7. **Deep Learning Classification with U-Net**
- A **U-Net mini model** is proposed for land cover classification.
- The training code is available in the **`unet_mini`** folder.
- The architecture was inspired by a **TensorFlow U-Net repository on GitHub** (unfortunately, the original repo is not available at the moment, but will be updated as soon as possible).
- I modified it so that id doesn't produce unnecessary patches like PNG files, but does everything in memory as numpy tables
- The patching is stratified (with sciki-learn), so the labels that are chosen are balanced
- The prediction is done so, that it finishes in a GRASS GIS database
- No extra documentation in the unet_folder, life is short and this week is even shorter :)

### 8. **Post-Processing in GRASS GIS: Change Detection and Area Calculation**
- The classification results are meant to be imported into a local **GRASS GIS** database to analyze changes in impervious land cover over time and create a table that the dashboard will fetch.
- Using **`r.mapcalc`**, changes are detected by identifying pixels that became impervious or green space in a new year but were not in the previous year. This is the logic and there is no bash code in this version.
  ```
  r.mapcalc "new_impervious_2023 = if(impervious_2023 == 1 && impervious_2022 == 0, 1, 0)"
  r.mapcalc "new_green_2023 = if(green_2023 == 1 && green_2022 == 0, 1, 0)"
  ```
- Next, zonal statistics were computed for each NUTS region using vector data:
  ```
  v.rast.stats map=NUTS_vector_dataset raster=new_impervious_2023 column_prefix=impervious_2023 method=sum
  v.rast.stats map=NUTS_vector_dataset raster=new_green_2023 column_prefix=green_2023 method=sum
  ```
- The results provided quantitative insights into the expansion or reduction of impervious surfaces and green spaces year-wise.
