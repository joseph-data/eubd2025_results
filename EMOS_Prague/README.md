# **Ice and Open Water Analysis for Norway Fjord and Finland Lake using Sentinel-1 IW**
This project aims to analyze ice and open water conditions in the Norway Fjord and Finland Lake regions using Sentinel-1 IW satellite data. The interactive dashboard visualizes key indicators including ice coverage, thickness variability, and temporal stability through comprehensive time series analysis. By leveraging SAR (Synthetic Aperture Radar) backscatter measurements, the system enables researchers to identify distinct patterns in ice formation, seasonal variations, and stability across these different water bodies.

The dashboard provides environmental scientists and water resource managers with a powerful tool to monitor ice dynamics over time, offering insights into how coastal fjords and inland lakes differ in their ice characteristics. This information is critical for climate research, winter transportation planning, and predicting future ice behavior. The comparative analysis features highlight regional differences in ice formation processes, stability zones, and seasonal transitions, contributing to a deeper understanding of how different water bodies respond to environmental factors.

## 3 Indicators Interpretation

**1. Ice Coverage Index**
\
$ICI = \frac{SIE_t - SIE_{t-1}}{SIE_{t-1}} \times 100$

- $SIE_t$ = Sea Ice Extent at time t
- $SIE_{t-1}$ = Sea Ice Extent at previous time (e.g., previous year or month)
- ICI = Percentage change in ice extent

Interpretation: The Ice Coverage Index represents the average SAR backscatter measurements across the monitored water body. Higher values (closer to 1.0) typically indicate more extensive ice coverage, while lower values (closer to 0.0) suggest more open water or thinner ice cover. This index provides insights into the extent and density of ice cover on the water surface, with seasonal trends showing increasing values during freezing periods and decreasing values during thaw.

**2. Ice Thickness Variability**

$h = A \cdot (\sigma_0^{VV} - \sigma_0^{VH}) + B$

- h = Ice thickness (meters)
- $\sigma_0^{VV}, \sigma_0^{VH}$ = SAR backscatter in VV and VH polarization
- A, B = Empirical coefficients based on field calibration

Interpretation: The Ice Thickness Variability index represents the standard deviation of SAR backscatter measurements, indicating how uniform or variable the ice thickness is across the monitored area. Higher values indicate more variable ice thickness or mixed ice conditions, while lower values suggest more uniform ice thickness or homogeneous surface conditions. This index helps identify areas with potential pressure ridges, cracks, or diverse ice formations that may impact navigation or infrastructure.

**3. Ice Temporal Stability**

$\frac{dC}{dt} = m$

- $\frac{dC}{dt}$ = Rate of change of sea ice concentration over time
- m = Slope of the linear regression line fitted to ice concentration data

Interpretation: The Ice Temporal Stability index represents the maximum SAR backscatter values observed, indicating the persistence and reliability of ice conditions over time. Higher values suggest more stable ice conditions that persist over longer periods, while lower values may indicate ephemeral ice formations or rapid changes in conditions. Tracking this index over seasons helps identify "stable ice zones" versus dynamic areas, which is crucial for winter transportation routes, ice fishing activities, and predicting future ice behavior for climate studies.
