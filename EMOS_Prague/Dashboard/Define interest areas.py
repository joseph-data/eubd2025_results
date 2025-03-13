# Example usage
norway_fjord_path = "mystorage/data/finland_lake.geojson"
finland_lake_path = "mystorage/data/norway_fjord.geojson"
river_gdf1 = gpd.read_file(norway_fjord_path)
river_gdf2 = gpd.read_file(finland_lake_path)
# Convert to EPSG 3035
river_gdf1 = river_gdf1.to_crs("EPSG:3035")
river_gdf2 = river_gdf2.to_crs("EPSG:3035")
# Geometry of an entire area
resolution = 20

data1 = json.load(open(norway_fjord_path, "r"))
data2 = json.load(open(finland_lake_path, "r"))

# Set center and zoom level
center = [60.78, 33.68]
zoom = 12

# Add OSM background
m1 = Map(basemap=basemaps.OpenStreetMap.Mapnik, center=center, zoom=zoom)

# Add geojson data
geo_json1 = GeoJSON(data=data1)
m1.add_layer(geo_json1)

# Display
m1

# Add OSM background
m2 = Map(basemap=basemaps.OpenStreetMap.Mapnik, center=center, zoom=zoom)

# Add geojson data
geo_json2 = GeoJSON(data=data2)
m2.add_layer(geo_json2)

# Display
m2

#Here, we can split the entire time period into 16 slots so that we can get 2 acquisitions every month to capture the freeze-thaw dynamics adequately.
start = datetime.datetime(2023, 9, 1)
end = datetime.datetime(2025, 3, 1)
n_chunks = 17
tdelta = (end - start) / n_chunks
edges = [(start + i * tdelta).date().isoformat() for i in range(n_chunks)]
slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

print("Monthly time windows:\n")
for slot in slots:
    print(slot)

#Requesting Sentinel-1 (SAR) Data
# SAR evalscript
evalscript_sar = """
function setup() {
  return {
    input: ["VV", "dataMask"],
    output: { bands: 2, sampleType: "FLOAT32"}
  }
}

// visualizes decibels from -20 to +10
function toDb(linear) {
  var log = 10 * Math.log(linear) / Math.LN10
  return Math.max(0, (log + 20) / 30)
}

function evaluatePixel(sample) {
  var VV = sample.VV;
  return [toDb(VV), sample.dataMask];
}
"""

# Modified SAR request function for Norway
def get_norway_sar_request(time_interval):
    # Calculate bounding box and appropriate dimensions
    bbox = river_gdf1.total_bounds
    bbox_width = bbox[2] - bbox[0]  
    bbox_height = bbox[3] - bbox[1] 
    
    # Calculate resolution that will keep us under 2500 pixels
    # Using max dimension to ensure neither width nor height exceeds the limit
    max_dimension = max(bbox_width, bbox_height)
    min_resolution = max_dimension / 2400  
    resolution = max(min_resolution, 20)
    
    print(f"Norway area dimensions: {bbox_width:.1f}m x {bbox_height:.1f}m")
    print(f"Using resolution of {resolution:.1f}m per pixel")
    
    return SentinelHubRequest(
        evalscript=evalscript_sar,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1_IW.define_from(
                    "s1iw", service_url=config.sh_base_url
                ),
                time_interval=time_interval,
                other_args={
                    "dataFilter": {
                        "resolution": "HIGH",
                        "mosaickingOrder": "mostRecent",
                        "orbitDirection": "ASCENDING",
                    },
                    "processing": {
                        "backCoeff": "SIGMA0_ELLIPSOID",
                        "orthorectify": True,
                        "demInstance": "COPERNICUS",
                        "speckleFilter": {
                            "type": "LEE",
                            "windowSizeX": 3,
                            "windowSizeY": 3,
                        },
                    },
                },
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        geometry=Geometry(river_gdf1.geometry.values[0], crs=river_gdf1.crs),
        resolution=(resolution, resolution), 
        config=config,
        data_folder="mystorage/results/norway",
    )

# Modified SAR request function for Finland
def get_finland_sar_request(time_interval):
    # Calculate bounding box and appropriate dimensions
    bbox = river_gdf2.total_bounds
    bbox_width = bbox[2] - bbox[0]  # in meters 
    bbox_height = bbox[3] - bbox[1]  # in meters
    
    # Calculate resolution that will keep us under 2500 pixels
    # Using max dimension to ensure neither width nor height exceeds the limit
    max_dimension = max(bbox_width, bbox_height)
    min_resolution = max_dimension / 2400      
    resolution = max(min_resolution, 20)
    
    print(f"Finland area dimensions: {bbox_width:.1f}m x {bbox_height:.1f}m")
    print(f"Using resolution of {resolution:.1f}m per pixel")
    
    return SentinelHubRequest(
        evalscript=evalscript_sar,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1_IW.define_from(
                    "s1iw", service_url=config.sh_base_url
                ),
                time_interval=time_interval,
                other_args={
                    "dataFilter": {
                        "resolution": "HIGH",
                        "mosaickingOrder": "mostRecent",
                        "orbitDirection": "ASCENDING",
                    },
                    "processing": {
                        "backCoeff": "SIGMA0_ELLIPSOID",
                        "orthorectify": True,
                        "demInstance": "COPERNICUS",
                        "speckleFilter": {
                            "type": "LEE",
                            "windowSizeX": 3,
                            "windowSizeY": 3,
                        },
                    },
                },
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        geometry=Geometry(river_gdf2.geometry.values[0], crs=river_gdf2.crs),
        resolution=(resolution, resolution), 
        config=config,
        data_folder="mystorage/results/finland",
    )
