import sqlite3
from ipyleaflet import basemaps

YEARS = list(range(2017, 2024))

BASEMAPS = {
    "WorldImagery": basemaps.Esri.WorldImagery,
}

INDICATORS = [
    {"rank": 1, "name": "Population Growth"},
    {"rank": 2, "name": "Urban Green Growth"},
    {"rank": 3, "name": "Floor Space"},
    {"rank": 4, "name": "Job Growth"},
]

def get_region_data(region_name, year, db_path="data.db"):
    """
    Retrieves actual indicator values for a given region and year from the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"""
    SELECT indicator, value FROM regional_data
    WHERE region_name = '{region_name}' AND year = {year}
    """

    cursor.execute(query)
    data = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return data

