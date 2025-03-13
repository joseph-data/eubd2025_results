library(sf)
library(leaflet)
library(leafem)
library(plotly)
library(plyr)
library(dplyr)


# Read the geojson-files containing the pollutants
demo0323 <- read_sf("~/0323demo.geojson")
demo0322 <- read_sf("~/0322demo.geojson")

# Read the geojson -file with NUTS3-geometries
pohjoismaat <- read_sf("~/pohjoismaaty.geojson") %>%
  dplyr::select(NUTS_ID, LEVL_CODE, CNTR_CODE, NAME_LATN, NUTS_NAME, URBN_TYPE, COAST_TYPE, lon, lat, geometry)
# Read the geojson -file with NUTS3-geometries
pohjoismaat_NUTS <- read_sf("~/pohjoismaaty.geojson") %>%
  dplyr::select(NUTS_ID, geometry)
# transform coordinate reference system to WGS84
demo0322 <- st_transform(demo0322, crs = '+proj=longlat +datum=WGS84')
demo0323 <- st_transform(demo0323, crs = '+proj=longlat +datum=WGS84')
pohjoismaat <- st_transform(pohjoismaat, crs = '+proj=longlat +datum=WGS84')

#Spatial join
demo0322_yhd <- st_join(demo0322, pohjoismaat_NUTS)
demo0323_yhd <- st_join(demo0323, pohjoismaat_NUTS)

# Pivot longer in order to calculate mean by NUTS3
demo0322_yhd_long <- st_drop_geometry(demo0322_yhd) %>%
  pivot_longer(cols = c(so2, co, ectot, no, no2, o3, pm10, sia), names_to = "luokka", values_to = "N") %>%
  filter(!is.na(NUTS_ID)) %>%
  group_by(NUTS_ID, luokka) %>%
  dplyr::summarize(ka=(mean(N)))

demo0323_yhd_long <- st_drop_geometry(demo0323_yhd) %>%
  pivot_longer(cols = c(so2, co, ectot, no, no2, o3, pm10, sia), names_to = "luokka", values_to = "N") %>%
  filter(!is.na(NUTS_ID)) %>%
  group_by(NUTS_ID, luokka) %>%
  dplyr::summarize(ka=(mean(N)))

# pivot back to wide for the join and export
demo0323_yhd_wide <- pivot_wider(demo0323_yhd_long, names_from = luokka, values_from = ka)

demo0322_yhd_wide <- pivot_wider(demo0322_yhd_long, names_from = luokka, values_from = ka)

# Join NUTS3-areas
pohjoismaat_0323 <- pohjoismaat %>%
  left_join(demo0323_yhd_wide, by=c("NUTS_ID"))
pohjoismaat_0322 <- pohjoismaat %>%
  left_join(demo0322_yhd_wide, by=c("NUTS_ID"))

st_write(pohjoismaat_0323, "~/pohjoismaat_0323.geojson")
st_write(pohjoismaat_0322, "~/pohjoismaat_0322.geojson")
