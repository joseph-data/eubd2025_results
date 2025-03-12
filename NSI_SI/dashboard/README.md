### This dashboard was made with Shiny for Python.

As it was done on a local environment, exact requirements are not available at the moment, but you can set them up step by step.

1. The dashboard can be run by executing `shiny run app.py`.
2. `shared.py` contains definitions for basemaps, data frame reading, and database connection.
3. `about.md` includes the information displayed in the dashboard.

## You can test this dashboard even without having data (and revamp it as much as you want to make cool things from it)
This is how it looks without data:

--photo--

### Database Connection
To retrieve real data, you need to connect the dashboard to an SQLite database. The database should contain a table named `regional_data` with the following structure (with examples):

**Table: `regional_data`**
| region_name       | year | indicator          | value |
|------------------|------|--------------------|-------|
| Zahodna Slovenija | 2023 | Floor Space        | 9.7   |
| Vzhodna Slovenija | 2023 | Job Growth         | 7.3   |

Make sure that your SQLite database (`data.db`) contains this table with correct NUTS region names (I mixed them all together, it's way simpler, but you can do it by NUTS_ID). The app retrieves data dynamically when a user clicks on a region in the map.
The SQLite database is used for prototyping. A real, complex one should be implemented using at least PostgreSQL or, even better, DuckDB.

This is how it looks with data:

--photo--

### To-Do
This prototype was made in a few days, and there is more to do. The major to-do is the correction of the data export process, depending on the API used for retrieval.
