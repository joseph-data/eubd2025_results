## PREPROCESSING AND IER FUNCTION README

### DOWNLOADING

Data is downloaded using the API of the CDSE platform and the CAMS databases.

The data used is the CAMS Air Quality Reanalysis database.

CAMS-AQR is highly processed data which the ECMWF produces based on Sentinel-5P, ground observations, and numerical modeling of the atmosphere.

For the code, see the file cdsapi_downloads.ipynb

The downloading code places intermediate netcdf files in downloadYYYY folders. Consider finding a better solution, since the process can take *hours*.

### PREPROCESSING

As if the cdsapi_downloads.ipynb notebook was not already enough of a monolith, sadly some the data preprocessing also happens there.

The particular steps taken is some aggregating (averaging) and combining different particle concentrations.

Finally, the processed data is moved to GeoJSON format.

### INTEGRATED EXPOSURE-RESPONSE FUNCTION

The IER function relates relative risk of death due to five diseases to ambient particulate matter. It is taken from literature and based on burden-of-disease calculation methods in use at the EPA, EEA and WHO.

The IER function and death estimates can be run in notebook estimate-mortality.ipynb.

As input, the notebook in its current state requires the files (documented elsewhere):

- pohjoismaat_0322.geojson
- pohjoismaat_0323.geojson
- estat_demo.pop.csv

As output, the notebook in its current state produces the files:

- pohjoismaat_0322-DEATHS.geojson
- pohjoismaat_0323-DEATHS.geojson

The IER code contains significant technical debt. The main issues are the following:

- The ambient particulate matter is currently averaged in a possibly improper manner.
- Different PM variables should not be summed together, but estimated into a "total" PM by some proper formula.
- The IER function just outright takes the parameter values alpha, beta, and gamma from a bayesian analysis done by the EPA, using file parameter_draws.csv.
- The disease base rates are just copied from Eurostat's publications.
- Deaths due to the different diseases (e.g. lung cancer, chronic pneumonia) are just summed together, but the relative risks correlate and thus should not be summed like this.

The steps to improve/fix this code, would be something like the following:

- Actually fit the IER function towards real data, e.g. the NUTS0 PM2.5 deaths, like the NSI Cyprus Team very wisely did.
- Add model parameters for how to weight time-of-day, instead of just crudely averaging over time.
- Check that the scientific background actually is correct (e.g. are different PM2.5 molecules "approximately exchangeable", or not?)
- Check how to sum the different causes of death properly.