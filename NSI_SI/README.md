## About LandPulse EU

### Description of the Prototype

**LandPulse EU** is an intuitive and data-driven prototype application designed to graphically visualise key indicators of land development and urban planning in the European Union. The application focuses on providing insights into how new impervious surfaces are connected to residential, environmental, and economic factors.

### New Indicators

1. **Population Growth**: Ratio of new impervious area rate (land consumption rate) to population growth rate (SGD 11.3.1; NUTS 2).
2. **Urban Green Growth**: Area of new impervious area per area of green urban spaces created (NUTS 2).
3. **Floor Space**: Area of new impervious land per useful floor area in building permits (for now, the only on NUTS 0).
4. **Job Growth**: Area of new impervious area per employment increase (NUTS 2).

### Background Idea

Land is a finite resource and the way it is used is one of the principal drivers of environmental change, through which land use has a significant impact on the quality of life and ecosystems. In Europe, the proportion of total land use occupied by production (agriculture, forestry, etc.) is one of the highest on the planet, and conflicting land-use demands require decisions that involve hard trade-offs.

Land use in Europe is driven by a number of factors, such as the increasing demand for living space per person, the link between economic activity, increased mobility, and the growth of transport infrastructure, which usually result in urban uptake.

The indicators attempt to:
- Create insights into how land consumption (new impervious surfaces) is connected to population growth.
- Evaluate the efficiency of land use for residential and non-residential buildings.
- Measure if green urban spaces increase or decrease in comparison to new impervious land.
- Assess land consumption per unit of floor area in building permits, using a three-year lag as a rough estimation of construction time.
- Understand the efficiency of land utilization in economic development by analyzing employment density.

### Indicator Descriptions

1. **Ratio of new impervious area rate to population growth rate**  
   The indicator is defined as the ratio of new impervious area rate to population growth rate.
   
2. **Area of new impervious area per area of green urban spaces created**  
   The indicator is defined as the ratio of new impervious area to green urban spaces area. 

3. **Area of new impervious land per useful floor area in building permits**  
   The indicator is defined as the ratio of new impervious area to building permit (m²) of usable area. 

4. **Area of new impervious area per employment increase**  
   The indicator is defined as the ratio of new impervious area to increase in employment.

### Data Sets

**Cloudless composites of Sentinel-2 SWIR 11, SWIR 12 and Band 4 (2017, 2018, 2019, 2020, 2021, 2022, 2023)**

**The Land Cover Map of Europe 2017 (S2GLC project) and CLC 2018**

We created a Deep Learning dataset for semantic segmentation using U-Net.
We created the labels by reclassfing the results of The Land Cover Map of Europe 2017 (S2GLC project) and combinign them with Sentinel-2 bands from the same year. We cleaned the results with CLC 2018.

Impervious Land Data Layer:


The basis of our new indicators are yearly impervious cover maps for the EU region. Maps are classified with deep learning. We created training and validation datasets (80-20 %) by modifying S2GLC project results from 2017 and combining them with cloudless composites that we built for 2017. The built model is ready to classify impervious lands for each new Sentinel-2 scene.

For the machine learning (ML) classification of land cover, we grouped the original 13 classes into three broader categories: Impervious, Green, and Other. After analyzing classification errors, we decided to include both Artificial surfaces and constructions and Natural material surfaces in the Impervious category. This decision was based on the observation that the ML model frequently misclassified Artificial surfaces and constructions as Natural material surfaces.

Since Natural material surfaces are generally stable over time, and our goal is to detect land cover changes, merging these two classes under Impervious improves the accuracy of change detection.

|          **Original classes**         |    **Reclassification**   |
|---------------------------------------|---------------------------|
| Artificial surfaces and constructions | Impervious land           |
| Cultivated                            | Green space               |
| Vineyards                             | Green space               |
| Herbaceous                            | Green space               |
| Deciduous                             | Green space               |
| Coniferous                            | Green space               |
| Moors and Heathland                   | Green space               |
| Sclerophyllous vegetation             | Green space               |
| Natural material surfaces             | Impervious land           |
| Permanent snow, glaciers              | Other                     |
| Marshes                               | Other                     |
| Peatbogs                              | Other                     |
| Water bodies                          | Other                     |

### Other Data Sets:
- Population density by NUTS 2 region, last update 26/03/2024.
- Building permits - annual data, last update 07/03/2025.
- Population on 1 January, last update 09/01/2025.
- Economically active population by sex, age and NUTS 2 region (1000), last update 12/12/2024.
- Degree of urbanization 2021.
- NUTS vector data 2024.

### Development tools and packages
Linux (OSGeoLive), Python (shiny, rasterio, pytorch, h5py, pandas, scikitlearn), GRASS GIS, GDAL, STAC.
Cloud Resorces of Creodias were used to process directly imagery from the S3 bucket.

---

This prototype provides a data-driven approach to guide sustainable urban planning and policy-making across the EU on a regional level.
