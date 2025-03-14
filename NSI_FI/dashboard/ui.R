
library(shinydashboard)
library(sf)
library(leaflet)
library(leafem)
library(plotly)
library(plyr)
library(dplyr)
library(tidyr)
library(data.table)


merkitl <- list("so2", "dust", "ectot", "no", "no2", "o3", "pm10", "sia")

ui <- dashboardPage(
  
  
  dashboardHeader(title = "AirX"),
  ## Sidebar content
  dashboardSidebar(
    sidebarMenu(
      menuItem("MapView", tabName = "dashboard", icon = icon("dashboard")),
      menuItem("Graphs & Table", tabName = "widgets", icon = icon("th")),
	  #radioButtons for population subgroup
      radioButtons("sex", label = h3("Choose a subgroup"), 
                   choices = list("Total" = "T:Total", "Male" = 'M:Males', "Female" = 'F:Females'),
                   selected ='T:Total'),
	  #radioButtons for years
      radioButtons("years", label = h3("Choose a Year"), 
                         choices = list("2022" = '2022', "2023" = '2023'),
                         selected ='2022'),
      
	  #select sentinel 5 layer
      selectInput( 
        "select", 
        "Select a pollutant for visualisation:", 
        choices = c("Sulfur dioxide" = "SO2",
                    "Nitrogen dioxide" = "NO2",
                    "Carbon monoxide" = "CO",
                    "Formaldehyde" = "HCHO",
                    "Ozone" = "O3",
                    "Methane" = "CH4",
                    "Aerosoles" = "AER_AI_340_380"), 
        multiple = FALSE 
      )
    ), 
    #show corine landcover legend from image in the web
    actionButton("show_image", "Corine Landcover Legend") ,
    
    
    # Downloadbutton
    downloadButton('download',"Download the data")
  ),
  ## Body content
  dashboardBody(
    tabItems(
      # First tab content
      tabItem(tabName = "dashboard",
              fluidRow(
                (leafletOutput("map", width = "100%", height = "900px")
                )
              )
      ),
      
      # Second tab content
      tabItem(tabName = "widgets",
              box(plotlyOutput("plot1", height = 400)),
              box(plotlyOutput("plot2", height = 400)),
              dataTableOutput('dto')
      )
    )
  )
)