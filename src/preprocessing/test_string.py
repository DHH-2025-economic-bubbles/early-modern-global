import geopandas as gpd

from settings import DATA_FOLDER


gdf = gpd.read_file(DATA_FOLDER / "filtered_places.gpkg")
country_places = set(gdf[gdf['country'] == "India"]['name'].tolist())
country_places.add("India".lower())

print(country_places)
string = "of june she left the lord walsingham la capt of in thur pundits capt the mab from bosnia and china the lord the half buy our labour all india union cap clark by was face arrived at st helena al anti expected to fail for bengal the i i the or lith a of june be letters recently received mention the death of of"

for country in country_places:
    if country in string:
        print("found")
        print(country)