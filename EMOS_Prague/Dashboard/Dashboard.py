import ipywidgets as widgets
from IPython.display import display, HTML
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import datetime
from pathlib import Path
import io
import base64

try:
    import ipywidgets
    import pandas
    import numpy
    import plotly
    import folium
    print("All required libraries are installed.")
except ImportError as e:
    print(f"Error: Missing library - {e}. Please run 'pip install ipywidgets pandas numpy plotly folium' to install.")
    exit()

# Generate sample data
def generate_sample_data():
    # Generate time slots
    start = datetime.datetime(2023, 9, 1)
    end = datetime.datetime(2025, 3, 1)
    n_chunks = 17
    tdelta = (end - start) / n_chunks
    edges = [(start + i * tdelta).date().isoformat() for i in range(n_chunks)]
    slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]
    
    # Create sample dataframes
    norway_data = []
    finland_data = []
    for slot in slots:
        start_date = slot[0]
        norway_data.append({
            'date': datetime.datetime.strptime(start_date, '%Y-%m-%d').date(),
            'mean': np.random.uniform(0.3, 0.7),
            'std': np.random.uniform(0.05, 0.2),
            'min': np.random.uniform(0.1, 0.3),
            'max': np.random.uniform(0.7, 0.9),
            'location': 'Norway Fjord'
        })
        finland_data.append({
            'date': datetime.datetime.strptime(start_date, '%Y-%m-%d').date(),
            'mean': np.random.uniform(0.3, 0.7),
            'std': np.random.uniform(0.05, 0.2),
            'min': np.random.uniform(0.1, 0.3),
            'max': np.random.uniform(0.7, 0.9),
            'location': 'Finland Lake'
        })
    
    norway_df = pd.DataFrame(norway_data)
    finland_df = pd.DataFrame(finland_data)
    combined_df = pd.concat([norway_df, finland_df])
    
    return combined_df

# Create map visualizations
def create_norway_map():
    """Create a folium map for Norway Fjord with satellite imagery"""
    try:
        # Coordinates for Sognefjord, Norway
        m = folium.Map(
            location=[61.1, 7.0], 
            zoom_start=6,
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        )
        
        # Add a polygon to represent the fjord area (in blue)
        folium.Polygon(
            locations=[
                [61.2, 6.8],
                [61.0, 6.8],
                [61.0, 7.2],
                [61.2, 7.2]
            ],
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.4,
            popup="Norway Fjord Study Area"
        ).add_to(m)
        
        # Add title
        title_html = '''
            <div style="position: fixed; 
                    top: 10px; left: 50px; width: 200px; height: 30px; 
                    background-color:white; border:2px solid grey; z-index:9999; 
                    font-size:16px; font-weight: bold;
                    text-align: center; padding: 5px;">
                Interactive Map
            </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map as HTML string
        map_html = m._repr_html_()
        return map_html
        
    except Exception as e:
        return f"<div style='padding: 20px; background-color: #f8d7da; color: #721c24;'>Error creating Norway map: {e}</div>"

def create_finland_map():
    """Create a folium map for Finland Lake with satellite imagery"""
    try:
        # Coordinates for Lake Saimaa, Finland
        m = folium.Map(
            location=[61.5, 28.5], 
            zoom_start=6,
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        )
        
        # Add a polygon to represent the lake area (in blue)
        folium.Polygon(
            locations=[
                [61.6, 28.3],
                [61.4, 28.3],
                [61.4, 28.7],
                [61.6, 28.7]
            ],
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.4,
            popup="Finland Lake Study Area"
        ).add_to(m)
        
        # Add title
        title_html = '''
            <div style="position: fixed; 
                    top: 10px; left: 50px; width: 200px; height: 30px; 
                    background-color:white; border:2px solid grey; z-index:9999; 
                    font-size:16px; font-weight: bold;
                    text-align: center; padding: 5px;">
                Interactive Map
            </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map as HTML string
        map_html = m._repr_html_()
        return map_html
        
    except Exception as e:
        return f"<div style='padding: 20px; background-color: #f8d7da; color: #721c24;'>Error creating Finland map: {e}</div>"

# Generate sample data
combined_df = generate_sample_data()

class IceWaterDashboard:
    def __init__(self, combined_df):
        self.combined_df = combined_df
        self.min_date = datetime.date(2023, 9, 1)
        self.max_date = datetime.date(2025, 3, 1)
        
        # Keep track of active selections
        self.active_main_section = "Statistical Overview"
        self.active_left_button = "Project Description"
        
        # For capturing export content
        self.current_figure = None
        
        # Create the main dashboard components
        self.create_widgets()
        
    def create_widgets(self):
        # Title row (first row)
        self.title = widgets.HTML(
            value="<h1 style='text-align: center; color: #2c3e50; margin-bottom: 20px;'>"
                  "Ice and Open Water Analysis for Norway Fjord and Finland Lake using Sentinel-1 IW</h1>"
        )
        
        # Time range and location selection (second row)
        self.location_dropdown = widgets.Dropdown(
            options=[('Norway Fjord', 'Norway Fjord'), ('Finland Lake', 'Finland Lake'), ('Both', 'both')],
            value='both',
            description='Location:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='200px')
        )
        
        self.start_date_picker = widgets.DatePicker(
            description='Start Date:',
            value=self.min_date,
            style={'description_width': 'initial'}
        )
        
        self.end_date_picker = widgets.DatePicker(
            description='End Date:',
            value=self.max_date,
            style={'description_width': 'initial'}
        )
        
        # Section title
        self.section_label = widgets.HTML(
            value="<div style='margin-bottom: 5px; font-weight: bold; font-size: 16px;'>Section:</div>"
        )
        
        # Four section buttons (third row)
        self.section_buttons = widgets.ToggleButtons(
            options=['Statistical Overview', 'Ice Coverage Index', 'Ice Thickness Variability', 'Ice Temporal Stability'],
            value='Statistical Overview',
            style={'button_width': 'auto', 'font_weight': 'bold'},
            button_style='info'
        )
        
        # View title
        self.view_label = widgets.HTML(
            value="<div style='margin-bottom: 5px; font-weight: bold; font-size: 16px;'>View:</div>"
        )
        
        # Left column buttons (vertical)
        self.left_buttons = widgets.RadioButtons(
            options=['Project Description', 'Map Location', 'SAR Backscatter Analysis', 'Comparison Analysis'],
            value='Project Description',
            style={'description_width': 'initial', 'button_color': '#3498db'},
            layout=widgets.Layout(width='250px')
        )
        
        # SAR indicator dropdown
        self.sar_indicator_dropdown = widgets.Dropdown(
            options=[
                ('Ice Coverage', 'mean'),
                ('Ice Thickness', 'std'),
                ('Temporal Stability', 'max')
            ],
            value='mean',
            description='Indicator:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='200px', display='none')  
        )
        
        # Export button for slides
        self.export_button = widgets.Button(
            description='Export for Slides',
            button_style='success',
            tooltip='Export current view for slides',
            icon='download',
            layout=widgets.Layout(width='150px')
        )
        self.export_button.on_click(self.on_export_button_clicked)
        
        # Export status message
        self.export_status = widgets.HTML("")
        
        # Main content output area (right side)
        self.main_output = widgets.Output(layout=widgets.Layout(height='500px', width='800px'))
        
        # Connect callbacks
        self.section_buttons.observe(self.on_section_change, names='value')
        self.left_buttons.observe(self.on_left_button_change, names='value')
        self.location_dropdown.observe(self.update_view, names='value')
        self.start_date_picker.observe(self.update_view, names='value')
        self.end_date_picker.observe(self.update_view, names='value')
        self.sar_indicator_dropdown.observe(self.update_view, names='value')
        
        # Initialize the first view
        self.on_section_change(None)
        self.on_left_button_change(None)
    
    def on_section_change(self, change):
        self.active_main_section = self.section_buttons.value
        
        # Update left buttons based on the active section
        if self.active_main_section == 'Statistical Overview':
            # For Statistical Overview, show Project Description as the first option
            self.left_buttons.options = ['Project Description', 'Map Location', 'SAR Backscatter Analysis', 'Comparison Analysis']
        else:
            # For other sections, change first option to Index Interpretation
            self.left_buttons.options = ['Index Interpretation', 'Map Location', 'SAR Backscatter Analysis', 'Comparison Analysis']
        
        # Set default value for left buttons based on new options
        if self.active_left_button not in [option for option in self.left_buttons.options]:
            self.active_left_button = self.left_buttons.options[0]
            self.left_buttons.value = self.active_left_button
        
        self.update_view(None)
    
    def on_left_button_change(self, change):
        self.active_left_button = self.left_buttons.value
        
        # Show/hide SAR indicator dropdown based on selection
        if self.active_left_button == 'SAR Backscatter Analysis':
            self.sar_indicator_dropdown.layout.display = 'block'
        else:
            self.sar_indicator_dropdown.layout.display = 'none'
            
        self.update_view(None)
    
    def on_export_button_clicked(self, b):
        """Handle export button click to save current view as HTML"""
        try:
            # Create filename based on current selections
            filename = f"export_{self.active_main_section.replace(' ', '_')}_{self.active_left_button.replace(' ', '_')}.html"
            
            # Generate HTML content based on the current view
            if self.active_left_button == 'Map Location':
                # For maps, we need to capture the HTML directly
                location = self.location_dropdown.value
                if location == 'both' or location == 'Norway Fjord':
                    html_content = create_norway_map()
                else:
                    html_content = create_finland_map()
                
                # Add a title to the HTML
                title = f"{self.active_main_section} - {self.active_left_button}"
                html_content = f"<h2>{title}</h2>\n{html_content}"
                
                # Create downloadable HTML
                b64_html = base64.b64encode(html_content.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64_html}" download="{filename}" target="_blank">Click to download {filename}</a>'
                
                self.export_status.value = (
                    f'<div style="padding: 10px; background-color: #d4edda; color: #155724; margin-top: 10px;">'
                    f'Export ready: {href}</div>'
                )
                
            elif self.current_figure:
                # For plotly figures, we can save them as HTML files
                html_content = self.current_figure.to_html(full_html=True, include_plotlyjs='cdn')
                
                # Create downloadable HTML
                b64_html = base64.b64encode(html_content.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64_html}" download="{filename}" target="_blank">Click to download {filename}</a>'
                
                self.export_status.value = (
                    f'<div style="padding: 10px; background-color: #d4edda; color: #155724; margin-top: 10px;">'
                    f'Export ready: {href}</div>'
                )
            else:
                self.export_status.value = (
                    f'<div style="padding: 10px; background-color: #f8d7da; color: #721c24; margin-top: 10px;">'
                    f'Nothing to export. Please generate a visualization first.</div>'
                )
                
        except Exception as e:
            self.export_status.value = (
                f'<div style="padding: 10px; background-color: #f8d7da; color: #721c24; margin-top: 10px;">'
                f'Error during export: {str(e)}</div>'
            )
    
    def update_view(self, change):
        # Clear main output
        with self.main_output:
            self.main_output.clear_output(wait=True)
            
            section = self.active_main_section
            view = self.active_left_button
            location = self.location_dropdown.value
            start_date = self.start_date_picker.value
            end_date = self.end_date_picker.value
            
            # Filter data by date and location
            filtered_df = self.combined_df[(self.combined_df['date'] >= start_date) & 
                                          (self.combined_df['date'] <= end_date)]
            
            if location != 'both':
                filtered_df = filtered_df[filtered_df['location'] == location]
            
            # Display the appropriate visualization based on section and view
            if view == 'Project Description':
                self.display_project_description()
            elif view == 'Index Interpretation':
                self.display_index_interpretation()
            elif view == 'Map Location':
                self.display_map(section, filtered_df, location)
            elif view == 'SAR Backscatter Analysis':
                self.display_sar_analysis(section, filtered_df)
            elif view == 'Comparison Analysis':
                self.display_comparison(section, filtered_df)
                
    def display_project_description(self):
        """Display the project description"""
        description = """
        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin: 10px;">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">Project Overview</h2>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                The project analyzes ice and open water conditions in Norway Fjord and Finland Lake using Sentinel-1 IW satellite data. 
                The dashboard visualizes key indicators including ice coverage, thickness variability, and temporal stability through 
                interactive time series analysis.
            </p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                The system compares SAR backscatter measurements between the two locations to identify patterns and differences in ice formation. 
                This tool provides environmental researchers with a comprehensive way to monitor and understand ice dynamics in these critical 
                water bodies over time.
            </p>
            <div style="margin-top: 20px; display: flex; justify-content: space-around;">
                <div style="text-align: center; width: 45%;">
                    <h4 style="color: #2980b9;">Norway Fjord</h4>
                    <p>61.1°N, 7.0°E</p>
                    <p>Focus: Coastal ice dynamics</p>
                </div>
                <div style="text-align: center; width: 45%;">
                    <h4 style="color: #2980b9;">Finland Lake</h4>
                    <p>61.5°N, 28.5°E</p>
                    <p>Focus: Lake ice formation</p>
                </div>
            </div>
        </div>
        """
        display(HTML(description))
        
        # Set current figure to None since we're displaying HTML content
        self.current_figure = None
    
    def display_index_interpretation(self):
        """Display interpretation information for the current index"""
        section = self.active_main_section
        
        if section == 'Ice Coverage Index':
            title = "Ice Coverage Index Interpretation"
            content = """
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                The <b>Ice Coverage Index</b> represents the mean SAR backscatter measurements across the monitored water body.
                This index indicates the extent and density of ice cover on the water surface.
            </p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                <b>How to interpret the index:</b>
                <ul>
                    <li>Higher values (closer to 1.0) typically indicate more extensive ice coverage.</li>
                    <li>Lower values (closer to 0.0) suggest more open water or thinner ice cover.</li>
                    <li>Seasonal trends show increasing values during freezing periods and decreasing values during thaw.</li>
                </ul>
            </p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                <b>Limitations:</b> SAR backscatter can be influenced by surface roughness, ice type, and weather conditions.
                Interpretation should consider these contextual factors.
            </p>
            """
        elif section == 'Ice Thickness Variability':
            title = "Ice Thickness Variability Interpretation"
            content = """
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                The <b>Ice Thickness Variability</b> index represents the standard deviation of SAR backscatter measurements.
                This metric indicates how uniform or variable the ice thickness is across the monitored area.
            </p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                <b>How to interpret the index:</b>
                <ul>
                    <li>Higher values indicate more variable ice thickness or mixed ice conditions.</li>
                    <li>Lower values suggest more uniform ice thickness or homogeneous surface conditions.</li>
                    <li>Increased variability often occurs during transition periods (freezing or thawing).</li>
                </ul>
            </p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                <b>Applications:</b> This index helps identify areas with potential pressure ridges, cracks,
                or diverse ice formations that may impact navigation or infrastructure.
            </p>
            """
        elif section == 'Ice Temporal Stability':
            title = "Ice Temporal Stability Interpretation"
            content = """
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                The <b>Ice Temporal Stability</b> index represents the maximum SAR backscatter values observed.
                This metric indicates the persistence and reliability of ice conditions over time.
            </p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                <b>How to interpret the index:</b>
                <ul>
                    <li>Higher values suggest more stable ice conditions that persist over longer periods.</li>
                    <li>Lower values may indicate ephemeral ice formations or rapid changes in conditions.</li>
                    <li>Tracking this index over seasons helps identify "stable ice zones" versus dynamic areas.</li>
                </ul>
            </p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                <b>Practical importance:</b> Temporal stability is crucial for winter transportation routes,
                ice fishing activities, and predicting future ice behavior for climate studies.
            </p>
            """
        else:
            title = "Index Interpretation"
            content = "<p>Please select a specific index section for interpretation details.</p>"
        
        # Create the HTML content
        interpretation = f"""
        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin: 10px;">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">{title}</h2>
            {content}
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                <h4 style="color: #2980b9;">Methodology Note</h4>
                <p style="font-size: 14px; font-style: italic;">
                    These indices are derived from Sentinel-1 IW SAR backscatter data, processed with temporal filtering
                    and radiometric calibration. The analysis compares Norway Fjord and Finland Lake to identify distinct 
                    patterns in ice formation, stability, and seasonal variations.
                </p>
            </div>
        </div>
        """
        
        display(HTML(interpretation))
        
        # Set current figure to None since we're displaying HTML content
        self.current_figure = None
    
    def display_map(self, section, filtered_df, location):
        """Display map visualization for the selected section"""
        # Display custom location selector for the map view
        map_location_dropdown = widgets.Dropdown(
            options=[('Norway Fjord', 'Norway Fjord'), ('Finland Lake', 'Finland Lake')],
            value='Norway Fjord' if location == 'both' or location == 'Norway Fjord' else 'Finland Lake',
            description='Location:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='200px')
        )
        
        def on_map_location_change(change):
            with self.main_output:
                self.main_output.clear_output(wait=True)
                # Re-display the dropdown
                display(map_location_dropdown)
                
                # Get the new location
                new_location = change['new']
                
                # Display the map based on the new location
                if new_location == 'Norway Fjord':
                    html_content = create_norway_map()
                else:  # Finland Lake
                    html_content = create_finland_map()
                
                # Display the map
                display(HTML(html_content))
                
                # Set current figure to None since we're not using Plotly for maps
                self.current_figure = None
        
        map_location_dropdown.observe(on_map_location_change, names='value')
        
        # Display the dropdown
        display(map_location_dropdown)
        
        # Display initial map
        if map_location_dropdown.value == 'Norway Fjord':
            html_content = create_norway_map()
        else:  # Finland Lake
            html_content = create_finland_map()
        
        display(HTML(html_content))
        
        # Set current figure to None since we're not using Plotly for maps
        self.current_figure = None
    
    def display_sar_analysis(self, section, filtered_df):
        """Display SAR backscatter analysis for the selected section"""
        indicator = self.sar_indicator_dropdown.value
        indicator_name = dict(mean='Ice Coverage', std='Ice Thickness', max='Temporal Stability')[indicator]
        
        # Special case for comparative SAR backscatter
        if section == 'Statistical Overview' and indicator == 'mean':
            # Create enhanced comparative SAR backscatter analysis
            fig = go.Figure()
            
            # Get data for each location - ensure we have data for both locations for comparison
            norway_df = filtered_df[filtered_df['location'] == 'Norway Fjord'].sort_values('date')
            finland_df = filtered_df[filtered_df['location'] == 'Finland Lake'].sort_values('date')
            
            # Add traces for Norway
            fig.add_trace(go.Scatter(
                x=norway_df['date'],
                y=norway_df['mean'],
                mode='lines+markers',
                name='Norway Fjord',
                marker=dict(symbol='circle', size=8),
                line=dict(width=2, color='navy')
            ))
            
            # Add traces for Finland
            fig.add_trace(go.Scatter(
                x=finland_df['date'],
                y=finland_df['mean'],
                mode='lines+markers',
                name='Finland Lake',
                marker=dict(symbol='square', size=8),
                line=dict(width=2, color='royalblue', dash='dash')
            ))
            
            fig.update_layout(
                title="Comparative SAR Backscatter: Norway Fjord vs Finland Lake",
                xaxis_title="Date",
                yaxis_title="Average Backscatter (scaled)",
                template='plotly_white',
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode="x unified"
            )
            
            # Add grid
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            
        elif section == 'Statistical Overview':
            # Box plot for other statistical overviews
            fig = px.box(filtered_df, y=[indicator], points='all', color='location',
                       labels={'value': indicator_name, 'variable': 'Metric'},
                       title=f"SAR Backscatter Analysis: {section}")
            
        elif section in ['Ice Coverage Index', 'Ice Thickness Variability', 'Ice Temporal Stability']:
            # Line plot for time series
            y_column = {'Ice Coverage Index': 'mean', 
                       'Ice Thickness Variability': 'std', 
                       'Ice Temporal Stability': 'max'}.get(section, indicator)
            
            # Create enhanced comparative graph for time series too
            fig = go.Figure()
            
            for loc in filtered_df['location'].unique():
                loc_df = filtered_df[filtered_df['location'] == loc].sort_values('date')
                
                marker_symbol = 'circle' if loc == 'Norway Fjord' else 'square'
                line_style = 'solid' if loc == 'Norway Fjord' else 'dash'
                line_color = 'navy' if loc == 'Norway Fjord' else 'royalblue'
                
                fig.add_trace(go.Scatter(
                    x=loc_df['date'],
                    y=loc_df[y_column],
                    mode='lines+markers',
                    name=loc,
                    marker=dict(symbol=marker_symbol, size=8),
                    line=dict(width=2, color=line_color, dash=line_style)
                ))
            
            fig.update_layout(
                title=f"SAR Backscatter Analysis: {section}",
                xaxis_title="Date",
                yaxis_title=section,
                template='plotly_white',
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode="x unified"
            )
            
            # Add grid
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            
        fig.update_layout(template='plotly_white', height=500)
        self.current_figure = fig
        display(fig)
    
    def display_comparison(self, section, filtered_df):
        """Display comparison analysis for the selected section"""
        title = f"Comparison Analysis: {section}"
        
        if section == 'Statistical Overview':
            # Radar chart comparison
            fig = go.Figure()
            
            for loc in filtered_df['location'].unique():
                loc_df = filtered_df[filtered_df['location'] == loc]
                mean_vals = [
                    loc_df['mean'].mean(),
                    loc_df['std'].mean(),
                    loc_df['max'].mean(),
                    loc_df['min'].mean()
                ]
                # Close the radar chart by repeating first value
                mean_vals.append(mean_vals[0])
                fig.add_trace(go.Scatterpolar(
                    r=mean_vals,
                    theta=['Ice Coverage', 'Ice Thickness', 'Temporal Stability', 'Minimum', 'Ice Coverage'],
                    fill='toself',
                    name=loc
                ))
                
            fig.update_layout(
                title=title,
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                    )
                ),
                showlegend=True,
                height=500
            )
            
        elif section == 'Ice Coverage Index':
            # Scatter plot of coverage vs time
            fig = px.scatter(filtered_df, x='date', y='mean', color='location', size='mean',
                           labels={'date': 'Date', 'mean': 'Ice Coverage', 'location': 'Location'},
                           title=title)
            fig.update_layout(height=500)
            
        elif section == 'Ice Thickness Variability':
            # Scatter plot of thickness vs coverage
            fig = px.scatter(filtered_df, x='mean', y='std', color='location', size='max',
                           labels={'mean': 'Ice Coverage', 'std': 'Ice Thickness', 'location': 'Location'},
                           title=title)
            fig.update_layout(height=500)
            
        elif section == 'Ice Temporal Stability':
            # Create separate histograms for each location (no overlay)
            fig = go.Figure()
            
            # Add Norway Fjord histogram
            norway_df = filtered_df[filtered_df['location'] == 'Norway Fjord']
            fig.add_trace(go.Histogram(
                x=norway_df['max'],
                name='Norway Fjord',
                marker=dict(color='rgba(100, 149, 237, 0.7)'),  # Cornflower blue
                xbins=dict(start=0.7, end=0.9, size=0.05)
            ))
            
            # Add Finland Lake histogram
            finland_df = filtered_df[filtered_df['location'] == 'Finland Lake']
            fig.add_trace(go.Histogram(
                x=finland_df['max'],
                name='Finland Lake',
                marker=dict(color='rgba(255, 99, 132, 0.7)'),  # Pinkish red
                xbins=dict(start=0.7, end=0.9, size=0.05)
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Temporal Stability",
                yaxis_title="Number of Observations",
                barmode='group',  # 'group' instead of 'overlay'
                template='plotly_white',
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
        
        fig.update_layout(template='plotly_white')
        self.current_figure = fig
        display(fig)
    
    def display_dashboard(self):
        # Time range and location selection row
        control_row = widgets.HBox([
            self.location_dropdown,
            self.start_date_picker,
            self.end_date_picker,
            self.sar_indicator_dropdown,
            self.export_button
        ])
        
        # Full dashboard layout
        dashboard = widgets.VBox([
            self.title,
            widgets.HTML("<hr style='margin: 5px 0;'>"),
            control_row,
            widgets.HTML("<hr style='margin: 5px 0;'>"),
            widgets.HBox([self.section_label, self.section_buttons], 
                       layout=widgets.Layout(align_items='center')),
            widgets.HTML("<hr style='margin: 5px 0;'>"),
            widgets.HBox([
                widgets.VBox([
                    self.view_label,
                    self.left_buttons
                ]),
                self.main_output
            ])
        ], layout=widgets.Layout(width='100%'))
        
        # Add export status at the bottom
        export_status_row = widgets.HBox([self.export_status], 
                                        layout=widgets.Layout(margin='10px 0 0 0'))
        dashboard.children = dashboard.children + (export_status_row,)
        
        display(dashboard)

# Generate sample data
combined_df = generate_sample_data()

# Create and display the dashboard
dashboard = IceWaterDashboard(combined_df)
dashboard.display_dashboard()
