import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from rasterio.features import rasterize

# ----- Mapping dictionary for CORINE to Ecosystem accounts -----
# (Using only the first element = level1 classification)
clc_to_ecosystem = {
    1: (1, 11),   # 111 - Continuous urban fabric
    2: (1, 12),   # 112 - Discontinuous urban fabric
    3: (1, 13),   # 121 - Industrial or commercial units
    4: (1, 13),   # 122 - Road and rail networks and associated land
    5: (1, 13),   # 123 - Port areas
    6: (1, 13),   # 124 - Airports
    7: (1, 13),   # 131 - Mineral extraction sites
    8: (1, 13),   # 132 - Dump sites
    9: (1, 13),   # 133 - Construction sites
    10: (1, 15),  # 141 - Green urban areas
    11: (1, 15),  # 142 - Sport and leisure facilities
    12: (2, 21),  # 211 - Non-irrigated arable land
    13: (2, 21),  # 212 - Permanently irrigated land
    14: (2, 21),  # 213 - Rice fields
    15: (2, 21),  # 221 - Vineyards
    16: (2, 23),  # 222 - Fruit trees and berry plantations
    17: (2, 23),  # 223 - Olive groves
    18: (3, 31),  # 231 - Pastures
    19: (2, 23),  # 241 - Annual crops associated with permanent crops
    20: (2, 25),  # 242 - Complex cultivation patterns
    21: (2, 25),  # 243 - Land principally occupied by agriculture with significant areas of natural vegetation
    22: (2, 25),  # 244 - Agro-forestry areas
    23: (4, 41),  # 311 - Broad-leaved forest
    24: (4, 42),  # 312 - Coniferous forest
    25: (4, 44),  # 313 - Mixed forest
    26: (3, 32),  # 321 - Natural grasslands
    27: (5, 52),  # 322 - Moors and heathland
    28: (5, 52),  # 323 - Sclerophyllous vegetation
    29: (4, 46),  # 324 - Transitional woodland-shrub
    30: (11, 112),# 331 - Beaches, dunes, sands
    31: (6, 61),  # 332 - Bare rocks
    32: (6, 62),  # 333 - Sparsely vegetated areas
    34: (6, 62),  # 335 - Glaciers and perpetual snow
    35: (7, 71),  # 411 - Inland marshes
    36: (7, 72),  # 412 - Peat bogs
    37: (11, 114),# 421 - Salt marshes
    38: (11, 114),# 422 - Salines
    39: (10, 101),# 423 - Intertidal flats
    40: (8, 82),  # 511 - Water courses
    41: (9, 92),  # 512 - Water bodies
    42: (10, 101), # 521 - Coastal lagoons
    43: (10, 101)  # 522 - Estuaries
}

# Create a mapping for level1 only (extract first element of each tuple)
clc_to_level1 = {clc: mapping[0] for clc, mapping in clc_to_ecosystem.items()}

def reclassify_raster_level1(input_raster, output_raster):
    """
    Reclassifies a large raster to level1 using windowed (block) processing to avoid high memory usage.
    """
    with rasterio.open(input_raster) as src:
        profile = src.profile.copy()
        nodata_value = src.nodata if src.nodata is not None else 0
        # Ensure nodata is within valid range (0-65535 for uint16)
        if nodata_value < 0 or nodata_value > 65535:
            nodata_value = 0

        # Update profile to use uint16, LZW compression, and proper nodata
        profile.update(dtype=rasterio.uint16, compress='lzw', nodata=nodata_value)

        with rasterio.open(output_raster, 'w', **profile) as dst:
            # Process the raster by its block windows to reduce memory usage
            for ji, window in src.block_windows(1):
                # Read the current window from the raster
                data = src.read(1, window=window).astype(np.int32)
                # Create an output array for this block filled with the nodata value
                level1_block = np.full(data.shape, fill_value=nodata_value, dtype=np.uint16)
                # For each CLC code, assign the corresponding level1 value using the mapping dictionary
                for clc_value, l1 in clc_to_level1.items():
                    mask = data == clc_value
                    level1_block[mask] = l1
                # Write the processed block to the output raster
                dst.write(level1_block, 1, window=window)
    return output_raster

def compute_zonal_stats(raster_file, geojson_file, zone_type='NUTS0'):
    """
    Computes area (in hectares) per ecosystem class within each zone.
    If the polygon’s bounding window is huge, the function subdivides it into smaller blocks to
    avoid excessive memory allocation.
    
    zone_type: 'NUTS0' for country-level (uses field "NUTS_NAME"),
               'NUTS2' for region-level (combines "CNTR_CODE" and "NUTS_NAME").
    """
    import rasterio
    from rasterio.windows import from_bounds, transform as window_transform_func, Window
    from rasterio.features import rasterize
    import geopandas as gpd
    import numpy as np
    import pandas as pd

    # Open the raster once to extract general info
    with rasterio.open(raster_file) as src:
        raster_crs = src.crs
        global_transform = src.transform
        nodata = src.nodata if src.nodata is not None else 0
        # Calculate pixel area (in hectares)
        pixel_area = abs(src.transform[0]) * abs(src.transform[4]) / 10000

        # Read the GeoJSON file and reproject if necessary
        gdf = gpd.read_file(geojson_file)
        if gdf.crs != raster_crs:
            gdf = gdf.to_crs(raster_crs)

        stats_list = []
        max_block = 1000  # maximum block size to process at one time
        for idx, row in gdf.iterrows():
            geom = row.geometry
            # Define zone name based on zone type
            if zone_type == 'NUTS0':
                zone_name = row.get('NUTS_NAME', f'zone_{idx}')
            elif zone_type == 'NUTS2':
                cntr = row.get('CNTR_CODE', '')
                nuts_name = row.get('NUTS_NAME', '')
                zone_name = f"{cntr}_{nuts_name}"
            else:
                zone_name = f'zone_{idx}'

            # Determine the window that covers the geometry bounds
            bounds = geom.bounds  # (minx, miny, maxx, maxy)
            window = from_bounds(*bounds, transform=global_transform)
            window = window.round_offsets().round_lengths()

            # Get window dimensions
            w_width = int(window.width)
            w_height = int(window.height)
            area_counts = {}  # accumulator for pixel counts for each ecosystem class

            if w_width > max_block or w_height > max_block:
                # Subdivide the window into smaller tiles
                for row_off in range(0, w_height, max_block):
                    for col_off in range(0, w_width, max_block):
                        tile_width = min(max_block, w_width - col_off)
                        tile_height = min(max_block, w_height - row_off)
                        # Create a sub-window relative to the full raster
                        tile_window = Window(window.col_off + col_off, window.row_off + row_off, tile_width, tile_height)
                        # Read only this tile
                        data_tile = src.read(1, window=tile_window, boundless=True, fill_value=nodata)
                        # Get transform for this tile
                        tile_transform = rasterio.windows.transform(tile_window, global_transform)
                        # Rasterize the geometry over this tile
                        out_shape = data_tile.shape
                        tile_mask = rasterize(
                            [(geom, 1)],
                            out_shape=out_shape,
                            transform=tile_transform,
                            fill=0,
                            dtype='uint8'
                        )
                        masked_tile = np.where(tile_mask == 1, data_tile, nodata)
                        valid_tile = masked_tile[masked_tile != nodata]
                        if valid_tile.size > 0:
                            unique, counts = np.unique(valid_tile, return_counts=True)
                            for k, c in zip(unique, counts):
                                area_counts[int(k)] = area_counts.get(int(k), 0) + c
            else:
                # Process the entire window at once
                data = src.read(1, window=window, boundless=True, fill_value=nodata)
                win_transform = window_transform_func(window, global_transform)
                out_shape = data.shape
                mask = rasterize(
                    [(geom, 1)],
                    out_shape=out_shape,
                    transform=win_transform,
                    fill=0,
                    dtype='uint8'
                )
                masked_data = np.where(mask == 1, data, nodata)
                valid_data = masked_data[masked_data != nodata]
                if valid_data.size > 0:
                    unique, counts = np.unique(valid_data, return_counts=True)
                    for k, c in zip(unique, counts):
                        area_counts[int(k)] = area_counts.get(int(k), 0) + c

            # Convert counts to area (in hectares)
            area_dict = {k: v * pixel_area for k, v in area_counts.items()}

            # Prepare result record for the zone
            result = {'Zone': zone_name}
            if zone_type == 'NUTS0':
                result['Country'] = zone_name
            elif zone_type == 'NUTS2':
                result['Region'] = zone_name
            for eco_class, area in area_dict.items():
                result[f'ECO_{eco_class}'] = area
            stats_list.append(result)
    df = pd.DataFrame(stats_list)
    return df

def ensure_numeric(df):
    for col in df.columns:
        if col.startswith('ECO_'):
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# ----- Function to compute differences between two zonal statistics tables -----
def compute_difference(df_2012, df_2018, key='Zone'):
    """
    Merges two dataframes (for 2012 and 2018) on the key and computes differences
    for all ecosystem columns as: (2018 - 2012).
    """
    df_merged = pd.merge(df_2012, df_2018, on=key, suffixes=('_2012', '_2018'), how='outer')
    diff_df = df_merged[[key]].copy()
    
    # Ensure numeric values for all relevant columns
    for col in df_merged.columns:
        if col.endswith('_2012') or col.endswith('_2018'):
            df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')

    # Compute differences
    for col in df_merged.columns:
        if col.endswith('_2012'):
            base = col[:-5]
            col2012 = col
            col2018 = base + '_2018'
            if col2018 in df_merged.columns:
                diff_df[base + '_Diff'] = df_merged[col2018].fillna(0) - df_merged[col2012].fillna(0)
    
    return diff_df

# ----- Process input rasters for each year -----
# According to your instructions the file for "year 2012" is:
raster_2012_input = "U2018_CLC2012_v2020_20u1.tif"
# and for "year 2018" is:
raster_2018_input = "U2018_CLC2018_v2020_20u1.tif"

raster_2012_output = "2012_level1_EA.tif"
raster_2018_output = "2018_level1_EA.tif"

print("Reclassifying rasters to level1 ...")
reclassify_raster_level1(raster_2012_input, raster_2012_output)
reclassify_raster_level1(raster_2018_input, raster_2018_output)

# ----- Compute zonal statistics based on geojson files -----
# Geojson files (ensure they are correctly formatted)
nuts0_file = "NUTS0_3M_EUROPE.geojson"  # Country-level boundaries; uses field NUTS_NAME
nuts2_file = "NUTS2_3M_EUROPE.geojson"  # Regional boundaries; combines CNTR_CODE and NUTS_NAME
print("Computing zonal statistics for NUTS0 (countries) ...")
stats_2012_country = compute_zonal_stats(raster_2012_output, nuts0_file, zone_type='NUTS0')
stats_2018_country = compute_zonal_stats(raster_2018_output, nuts0_file, zone_type='NUTS0')

# Ensure numeric types
stats_2012_country = ensure_numeric(stats_2012_country)
stats_2018_country = ensure_numeric(stats_2018_country)

diff_country = compute_difference(stats_2012_country, stats_2018_country, key='Zone')

print("Computing zonal statistics for NUTS2 (regions) ...")
stats_2012_nuts2 = compute_zonal_stats(raster_2012_output, nuts2_file, zone_type='NUTS2')
stats_2018_nuts2 = compute_zonal_stats(raster_2018_output, nuts2_file, zone_type='NUTS2')

# Ensure numeric types
stats_2012_nuts2 = ensure_numeric(stats_2012_nuts2)
stats_2018_nuts2 = ensure_numeric(stats_2018_nuts2)

diff_nuts2 = compute_difference(stats_2012_nuts2, stats_2018_nuts2, key='Zone')

# Define ecosystem class renaming and sorting
ecosystem_classes = {
    1: '1 - Settlements and other artificial areas',
    2: '2 - Cropland',
    3: '3 - Grassland',
    4: '4 - Forest and woodland',
    5: '5 - Heathland and shrub',
    6: '6 - Sparsely vegetated ecosystems',
    7: '7 - Inland wetlands',
    8: '8 - Rivers and canals',
    9: '9 - Lakes and reservoirs',
    10: '10 - Marine inlets and transitional waters',
    11: '11 - Coastal beaches, dunes and wetlands'
}

def sort_and_rename(df, zone_type='Country'):
    # Sort by zone name if available, otherwise by 'Zone'
    sort_column = zone_type if zone_type in df.columns else 'Zone'
    df = df.sort_values(by=sort_column)
    
    # Prepare column order
    base_cols = ['Zone']
    if zone_type in df.columns:
        base_cols.append(zone_type)
    
    eco_cols = [f'ECO_{k}' for k in range(1, 12) if f'ECO_{k}' in df.columns]
    diff_cols = [f'ECO_{k}_Diff' for k in range(1, 12) if f'ECO_{k}_Diff' in df.columns]
    
    # Rename ecosystem columns
    rename_dict = {}
    for k, name in ecosystem_classes.items():
        rename_dict[f'ECO_{k}'] = name
        rename_dict[f'ECO_{k}_Diff'] = name + ' Diff'
    
    df = df.rename(columns=rename_dict)
    
    # Reorder columns if they exist
    ordered_cols = [col for col in base_cols if col in df.columns] + \
                   [rename_dict[col] for col in eco_cols if col in rename_dict] + \
                   [rename_dict[col] for col in diff_cols if col in rename_dict]
    
    df = df[ordered_cols]
    
    return df

def add_totals(df):
    # Total column per row (across ecosystem columns)
    # Identify columns that represent ecosystem areas (they start with a digit and contain ' - ')
    eco_cols = [col for col in df.columns if isinstance(col, str) and col[0].isdigit() and "Diff" not in col]
    df['Total'] = df[eco_cols].sum(axis=1)
    
    # Total row (sum of columns)
    total_row = {col: df[col].sum() if df[col].dtype != 'object' else 'Total' for col in df.columns}
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    
    return df

# ----- New function: add share columns for each ecosystem -----
def add_share_columns(df):
    # For each ecosystem column (not including diff or non-numeric fields),
    # compute share as (ecosystem area / Total) * 100.
    # We use the expected ecosystem names from ecosystem_classes.
    for k, eco_name in ecosystem_classes.items():
        if eco_name in df.columns:
            share_col = eco_name + " Share"
            # Use numpy where to avoid division by zero
            df[share_col] = np.where(df["Total"] != 0, df[eco_name] / df["Total"] * 100, 0)
    return df

# Apply sorting and renaming
stats_2012_country = sort_and_rename(stats_2012_country, zone_type='Country')
stats_2018_country = sort_and_rename(stats_2018_country, zone_type='Country')
diff_country = sort_and_rename(diff_country, zone_type='Country')

stats_2012_nuts2 = sort_and_rename(stats_2012_nuts2, zone_type='Region')
stats_2018_nuts2 = sort_and_rename(stats_2018_nuts2, zone_type='Region')
diff_nuts2 = sort_and_rename(diff_nuts2, zone_type='Region')

# Add total rows and columns
stats_2012_country = add_totals(stats_2012_country)
stats_2018_country = add_totals(stats_2018_country)
diff_country = add_totals(diff_country)

stats_2012_nuts2 = add_totals(stats_2012_nuts2)
stats_2018_nuts2 = add_totals(stats_2018_nuts2)
diff_nuts2 = add_totals(diff_nuts2)

# ---- NEW: Add share columns (percentage share of each ecosystem) for 2012 and 2018 stats ----
stats_2012_country = add_share_columns(stats_2012_country)
stats_2018_country = add_share_columns(stats_2018_country)
stats_2012_nuts2 = add_share_columns(stats_2012_nuts2)
stats_2018_nuts2 = add_share_columns(stats_2018_nuts2)

# ----- Export results to an Excel workbook -----
output_excel = "ecosystem_areas_comparison.xlsx"
with pd.ExcelWriter(output_excel) as writer:
    stats_2012_country.to_excel(writer, sheet_name="Country_2012", index=False)
    stats_2018_country.to_excel(writer, sheet_name="Country_2018", index=False)
    diff_country.to_excel(writer, sheet_name="Country_Diff", index=False)
    stats_2012_nuts2.to_excel(writer, sheet_name="NUTS2_2012", index=False)
    stats_2018_nuts2.to_excel(writer, sheet_name="NUTS2_2018", index=False)
    diff_nuts2.to_excel(writer, sheet_name="NUTS2_Diff", index=False)

def export_geojson(geojson_input, df, output_file, zone_type='NUTS0'):
    gdf = gpd.read_file(geojson_input)

    if zone_type == 'NUTS0':
        gdf['Zone'] = gdf['NUTS_NAME']
    elif zone_type == 'NUTS2':
        gdf['Zone'] = gdf['CNTR_CODE'] + '_' + gdf['NUTS_NAME']

    # Remove total row
    df = df[df['Zone'] != 'Total']

    # Optionally drop 'Total' column if present
    if 'Total' in df.columns:
        df = df.drop(columns=['Total'])

    # Merge attributes
    gdf = gdf.merge(df, on='Zone', how='left')

    gdf.to_file(output_file, driver='GeoJSON')

export_geojson(nuts0_file, stats_2012_country, 'Country_2012.geojson', zone_type='NUTS0')
export_geojson(nuts0_file, stats_2018_country, 'Country_2018.geojson', zone_type='NUTS0')
export_geojson(nuts0_file, diff_country, '2018_2012_Country_Diff.geojson', zone_type='NUTS0')

export_geojson(nuts2_file, stats_2012_nuts2, 'NUTS2_2012.geojson', zone_type='NUTS2')
export_geojson(nuts2_file, stats_2018_nuts2, 'NUTS2_2018.geojson', zone_type='NUTS2')
export_geojson(nuts2_file, diff_nuts2, '2018_2012_NUTS2_Diff.geojson', zone_type='NUTS2')

print("Processing complete. New TIFF files, Excel report, and GeoJSON outputs with share columns generated.")
