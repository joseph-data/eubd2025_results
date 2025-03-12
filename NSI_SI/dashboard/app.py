import math
import geopandas as gpd
from shapely.geometry import shape, Point
import ipyleaflet as L
from ipywidgets import Layout

# Shiny express
from shiny.express import ui, input, render
from shinywidgets import render_widget
from shiny import reactive
import plotly.graph_objects as go

# Import shared data
from shared import BASEMAPS, INDICATORS, YEARS, get_region_data

ui.page_opts(title="LandPulse EU: Impervious Land Footprints", fillable=True)
{"class": "bslib-page-dashboard"}

selected_region = reactive.Value()
global_map = None

# -- MAIN LAYOUT: Two columns: left for map, right for charts --
with ui.layout_columns(col_widths=(6, 6)):
    # ======== LEFT COLUMN: Map ========
    with ui.layout_column_wrap(width="100%"):
        with ui.card():
            ui.card_header("Map & Settings")
            ui.markdown("Click on the region of your choice")

            @render_widget
            def map_widget():
                global global_map
                if global_map is None:
                    global_map = L.Map(
                        center=(50, 10),
                        zoom=4,
                        scroll_wheel_zoom=True,
                        layout=Layout(width="100%", height="550px")
                    )
                    global_map.fit_bounds([
                        [30.1228755489397990, -41.9663128284834031],
                        [62.8570380621351035, 75.7120538158074936],
                    ])

                    for name, bmap_def in BASEMAPS.items():
                        tile_layer = L.basemap_to_tiles(bmap_def)
                        tile_layer.name = name
                        tile_layer.base = True
                        global_map.add_layer(tile_layer)

                    global_map.add_control(L.LayersControl(position="topright"))

                    geojson_layer = L.GeoJSON(
                        data=display_geojson(),
                        style={"color": "purple", "opacity": 0.5, "fillOpacity": 0.3}
                    )
                    global_map.add_layer(geojson_layer)
                    global_map.geojson_layer = geojson_layer

                    def handle_map_click(**kwargs):
                        if kwargs.get("type") != "click":
                            return
                        coords = kwargs.get("coordinates")
                        if not coords:
                            return
                        lat, lon = coords

                        gjson = display_geojson()
                        pt = Point(lon, lat)
                        found = None
                        for feat in gjson.get("features", []):
                            if shape(feat["geometry"]).contains(pt):
                                found = feat
                                break
                        if found:
                            selected_region.set(found["properties"])
                            geojson_layer.data = gjson

                    global_map.on_interaction(handle_map_click)

                return global_map

    # ======== RIGHT COLUMN: Tabs for Charts ========
    with ui.layout_column_wrap(width="100%"):
        with ui.card():
            ui.card_header("Data Analysis")
            with ui.navset_tab(id="tab"):
                with ui.nav_panel("Impervious Expansion and"):
                    ui.input_slider("year_slider", "Year:", min=2018, max=YEARS[-1], value=2023)
                    @render_widget
                    def spider_chart():
                        return spider_figure()

                with ui.nav_panel("Impervious Expansion Indicators Time Series"):
                    @render_widget
                    def time_series_chart():
                        return time_series_figure()

                with ui.nav_panel("Export Data"):
                    ui.markdown("Export your results in various formats.")
                    with ui.layout_column_wrap():
                        ui.input_action_button("export_plots", "Export Plots", width="100%")
                        ui.input_action_button("export_table", "Export Table", width="100%")
                        ui.input_action_button("export_map", "Export Raw Impervious Map", width="100%")

                with ui.nav_panel("About"):
                    ui.markdown(open("about.md").read())

# ---------------------
# Chart functions
# ---------------------

def spider_figure():
    region = selected_region()
    if not region:
        return go.Figure()

    selected_year = input.year_slider() if input.year_slider() else 2023
    region_name = region.get("NUTS_NAME", "Unknown Region")

    stats_vals = get_region_data(region_name, selected_year)
    if not stats_vals:
        return go.Figure()

    labels = list(stats_vals.keys())
    values = list(stats_vals.values())
    labels.append(labels[0])
    values.append(values[0])

    fig = go.Figure([
        go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            hovertemplate="%{theta}: %{r:.2f}<extra></extra>"
        )
    ])
    return fig


def time_series_figure():
    region = selected_region()
    if not region:
        return go.Figure()

    region_name = region.get("NUTS_NAME", "Unknown Region")
    x_years = YEARS
    fig = go.Figure()

    for ind in INDICATORS:
        indicator_name = ind["name"]
        y_vals = [get_region_data(region_name, year).get(indicator_name, None) for year in x_years]

        if any(y_vals):
            fig.add_trace(go.Scatter(
                x=x_years, y=y_vals, mode="lines+markers",
                name=indicator_name,
                hovertemplate="Year %{x}: %{y}<extra></extra>"
            ))

    return fig

@reactive.Calc
def display_geojson():
    gdf = gpd.read_file("data/NUTS012_RG_03M_2024_4326.geojson")
    gdf_filtered = gdf[gdf["LEVL_CODE"] == 2]
    return gdf_filtered.__geo_interface__

