import pymongo
import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json
import unicodedata


def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def do_stuff():  # placeholder

    password = "test_read"
    myclient = pymongo.MongoClient(f"mongodb+srv://test_read:{password}"
                                   f"@jobanalyzer.vydrnyx.mongodb.net/?retryWrites=true&w=majority")
    mydb = myclient["jobAnalyzer"]
    mycol = mydb["it software_jobs"]

    locations = []

    location_numbers = {}

    keyword = "english"

    #for col in mycol.find({"keywords": keyword}, {"location": 1}):  # keyword search
    #    if col["location"] is not None:
    #        locations.append(strip_accents(col["location"].replace(",", "")))

    for col in mycol.find():  # show all job listings regardless of keyword
        if col["location"] is not None:
            locations.append(strip_accents(col["location"].replace(",", "")))

    for location in locations:
        if location not in location_numbers:
            location_numbers[location] = locations.count(location)

    list_of_cities = list(location_numbers.keys())
    list_of_values = list(location_numbers.values())

    # TODO make values actually work, for it does not work now

    mycol2 = mydb["cities"]
    for i in range(len(list_of_cities)):  # map with city translation table
        print(f"City before translating to county: {list_of_cities[i]}")
        city = mycol2.find_one({"cities" : list_of_cities[i]}, {"_id":0, "County":1})
        if city is not None:
            list_of_cities[i] = city['County']
            print(f"County after translation:{city['County']}")

    list_of_counties = ["Cluj", "Maramures", "Satu Mare", "Salaj", "Alba", "Brasov", "Covasna", "Harghita", "Mures",
                        "Sibiu", "Bacau", "Botosani", "Iasi", "Neamt", "Suceava", "Vaslui", "Braila", "Buzau",
                        "Constanta", "Galati", "Tulcea", "Vrancea", "Arges", "Calarasi", "Dambovita", "Giurgiu",
                        "Ialomita", "Prahova", "Teleorman", "Bucuresti", "Ilfov", "Dolj", "Gorj", "Mehedinti", "Olt",
                        "Valcea", "Arad", "Caras-Severin", "Hunedoara", "Timis", "Bistrita-Nasaud", "Bihor"]

    for county in list_of_counties:
        if county not in list_of_cities:
            list_of_cities.append(county)

    print(list_of_values)
    print(f"Len values: {len(list_of_values)}")
    print(f"Len cities: {len(list_of_cities)}")

    while len(list_of_values) != len(list_of_cities):
        list_of_values.append(0)

    print(f"Len values: {len(list_of_values)}")
    print(f"Len cities: {len(list_of_cities)}")

    data = {"Counties": list_of_cities, "Values": list_of_values}


    pandas_dataframe = pd.DataFrame.from_dict(data)



    #fig = px.bar(pandas_dataframe, x='Cities', y='Values')
    #fig.write_html(file="test3.html", include_plotlyjs="cdn", full_html=False)

    df = pandas_dataframe.drop_duplicates(subset="Counties")
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.precision', 3,
                           ):
        print(df)
    with urlopen('https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/romania.geojson') as response:
        counties = json.load(response)
    #print(counties["features"][0])
    print(len(counties))


    fig = px.choropleth(df, geojson=counties, locations="Counties", scope="europe", color="Values",
                        color_continuous_scale="Thermal",
                        featureidkey='properties.name')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_geos(
        visible=True, resolution=110, scope="europe",
        showcountries=False, countrycolor="Black",
        showsubunits=False, subunitcolor="Blue",
        fitbounds="geojson"
    )
    fig.show()
    fig.write_html("jobs.html", include_plotlyjs='cdn')

