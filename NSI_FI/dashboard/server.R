library(shiny)
library(sf)
library(leaflet)
library(leafem)
library(plotly)
library(plyr)
library(dplyr)
library(tidyr)
library(data.table)
library(raster)
library(ggplot2)




# read geojsons for year 22 and 23 containing excess deaths by NUTS3 regions and population subgroups 

data_map22 <- read_sf("./pohjoismaat_0322-DEATHS.geojson") %>%
  mutate(year='2022')
data_map23 <- read_sf("./pohjoismaat_0323-DEATHS.geojson") %>%
  mutate(year='2023')

# bind year 22 and 23 to the same data
data_map <- rbind(data_map22,data_map23)

#Snapshots of the following tiff-files, visualisation purposes only
NO2 <- raster("./NO2.tiff")
CH4 <- raster("./CH4.tiff")
AER_AI_340_380 <- raster("./AER_AI_340_380.tiff")
CO <- raster("./CO.tiff")
O3 <- raster("./O3.tiff")
SO2 <- raster("./SO2.tiff")
HCHO <- raster("./HCHO.tiff")


# Transform to wgs84 projection 
data_map <- st_transform(data_map, crs = '+proj=longlat +datum=WGS84')

#drop geometry to turn into tibble for graphs and table
data_map2 <- st_drop_geometry(data_map) %>%
  dplyr::select(NUTS_ID, CNTR_CODE, NUTS_NAME, so2, ectot, no, no2, o3, pm10, sia, deaths, year, sex)


#pivot longer for visualisation purposes
data_map2_long <- data_map2 %>%
  pivot_longer(cols = c(so2, ectot, no, no2, o3, pm10, sia, deaths), names_to = "pollutant", values_to = "N") %>%
  mutate(N=round(N/12), digits=0)


server <- function(input, output) {

# reference to the Corine land cover wms
  observeEvent(input$show_image, {
    showModal(modalDialog(
      title = "Corine Land Cover Legend",
      img(src = "https://www.eea.europa.eu/data-and-maps/figures/corine-land-cover-1990-by-country/legend/image_large", width = "400px"),
      easyClose = TRUE,
      footer = NULL
    ))
  })
  
 #reactive filter for the spatial layer by year and population Subgroup
  data_map0 <- reactive({
    data_map %>%
      filter(year == input$years, sex == input$sex)%>%
      mutate(deaths=round(deaths/12,digits=0))
  })
 
 #leaflet 
  output$map <- renderLeaflet({


	#select deaths -variable from the data_map0 data frame
    selected_data <- data_map0()[['deaths']]
    
    wms_corinne <- "https://image.discomap.eea.europa.eu/arcgis/services/Corine/CLC2018_WM/MapServer/WmsServer"  
    # Compute dynamic bins based on the range of the selected data
    bins <- c(min(selected_data, na.rm = TRUE), 
              quantile(selected_data, probs = seq(0, 1, length.out = 8), na.rm = TRUE), 
              max(selected_data, na.rm = TRUE))
    
    # Remove duplicate bins
    bins <- unique(bins)
    # Create a color palette for excess deaths
	pal <- colorBin("Blues", domain = data_map0()[['deaths']], bins = bins)
    # Create a color palette for the sentinel 5 earth observations
    pal2 <- colorNumeric("Reds", values(get(input$select)), na.color = "transparent")
	# Create labels
    labels <- sprintf(
      "<strong>%s</strong><br/>%g Excessive Deaths</sup>",
      data_map0()$NUTS_NAME, data_map0()[['deaths']]
    ) %>% lapply(htmltools::HTML)

    
    leaflet() %>%

      setView(lng = 20.47247, lat = 62.78864, zoom = 5) %>% # zoom level and center point of the zoom
      addMapPane("background_map", zIndex = 410) %>%  # Level 1: bottom
      addMapPane("corine", zIndex = 411) %>%          # Level 1.5: bottom2
      addMapPane("polygons", zIndex = 420) %>%        # Level 2: middle
      addMapPane("labels", zIndex = 430) %>%          # Level 3: top
      addProviderTiles(providers$OpenStreetMap,options = , pathOptions(pane = "background_map")) %>% # add background
      addTiles() %>%
      addWMSTiles( wms_corinne, layers = "12",
                   options = WMSTileOptions(format = "image/png", transparent = T),pathOptions(pane = "corine"),group="corine") %>% # add wms tiles
      addRasterImage(get(input$select), colors = pal2, opacity = 0.3, group="Concentration", options = pathOptions(pane = "labels")) %>% # add sentinel 5 earth observations
      addLegend(pal = pal2, values = values(get(input$select)), title = "Pollutant Concentration") %>% # add legend for sentinel5
      addPolygons(data=data_map0(),  fillColor = ~pal(get('deaths')), # add polygon layer
                  weight = 2,
                  opacity = 1,
                  color = "white",
                  dashArray = "3",
                  fillOpacity = 0.3,
                  highlightOptions = highlightOptions(
                    weight = 5,
                    color = "#666",
                    dashArray = "",
                    fillOpacity = 0.5,
                    bringToFront = FALSE),
                  label = labels,
                  labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"
                    ),
                  ,group="Deaths"
                  ,options = pathOptions(pane = "polygons")) %>%
      addLegend(pal = pal, values = data_map0()[['deaths']], title = "Excessive Deaths per year") %>% # add legend for polygons 

      addLayersControl(
        baseGroups = c("Layers"),
        overlayGroups = c("Concentration", "Deaths", "corine"),
        options = layersControlOptions(collapsed = FALSE, autoZIndex = FALSE) # add control for the layers
      ) 
  })
  # filter and select reactively data for the first graph
  dat <- reactive({
    data_map2_long %>%
      filter(pollutant %in% 'deaths', sex == input$sex) %>%
      group_by(pollutant, CNTR_CODE, year) %>%
      dplyr::summarize(NN = sum(N)) 
  })
  # output and make the first graph
  output$plot1 <- renderPlotly({
    plot <- plot_ly(dat(), x = ~year, y = ~NN, type = 'bar', color=~CNTR_CODE) %>%
      layout(
        title = "Excess deaths by country",
        xaxis = list(title = "Country"),
        yaxis = list(title = "Amount of Excess Deaths")
      )
    plot
  })
  # filter and select reactively data for the second graph
  dat2 <- reactive({
    data_map2_long %>%
      filter(pollutant %in% 'deaths', sex == input$sex) %>%
      group_by(pollutant, NUTS_NAME, year) %>%
      dplyr::summarize(NN = sum(N))
  })
  # output and make the second graph
  output$plot2 <- renderPlotly({
    plot <- plot_ly(dat2(), x = ~year, y = ~NN, type = 'bar', color=~NUTS_NAME) %>%
      layout(
        title = "Excess deaths by country by NUTS area",
        xaxis = list(title = "Nuts Region"),
        yaxis = list(title = "Amount of Excess Deaths")
      )
    plot
  })
   # filter and select reactively data for the table 
  dat1 <- reactive({
    data_map2_long %>%
      filter(pollutant %in% 'deaths') %>%
      mutate(sex=substring(sex,3,))%>%
      dplyr::select(NUTS_ID, CNTR_CODE, NUTS_NAME, year, sex, N)
  })
  # output the tabular data
  output$dto <- renderDataTable({ dat1() }, options = list(pageLength = 10,
                                                           columns = list(
                                                             list(title = 'NUTS'),
                                                             list(title = 'Country Code'),
                                                             list(title = 'NUTS Name'),
                                                             list(title = 'Year'),
                                                             list(title = 'Subgroup'),
                                                             list(title = 'Excessive Deaths'))))
                                #colnames = c("NUTS ID", "Country Code", "NUTS Name", "Year", "Subgroup", "Excessive Deaths"))
  
  # output the tabular data to csv. Name of the csv is thename.csv
  output$download <- downloadHandler(
    filename = function() { "thename.csv" },
    content = function(fname) {
      write.csv(dat1(), fname)
    }
  )
}

