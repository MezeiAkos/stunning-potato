import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from urllib.request import urlopen
import json
import unicodedata
import numpy as np
from IPython.display import display

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

password = input("Password: ")
myclient = pymongo.MongoClient(f"mongodb+srv://Admin:{password}"
                                   f"@jobanalyzer.vydrnyx.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["jobAnalyzer"]
mycol = mydb["jobs"]

list_of_counties = ["Cluj", "Maramures", "Satu Mare", "Salaj", "Alba", "Brasov", "Covasna", "Harghita", "Mures",
                    "Sibiu", "Bacau", "Botosani", "Iasi", "Neamt", "Suceava", "Vaslui", "Braila", "Buzau",
                    "Constanta", "Galati", "Tulcea", "Vrancea", "Arges", "Calarasi", "Dambovita", "Giurgiu",
                    "Ialomita", "Prahova", "Teleorman", "Bucuresti", "Ilfov", "Dolj", "Gorj", "Mehedinti", "Olt",
                    "Valcea", "Arad", "Caras-Severin", "Hunedoara", "Timis", "Bistrita-Nasaud", "Bihor"]

list_of_industries = ['alimentara', 'asigurari-', 'banci---servicii-financiare', 'call-center---bpo', 'comert---retail',
                      'constructii', 'educatie---training', 'energetica', 'farma', 'it---telecom', 'masini---auto',
                      'media---internet', 'medicina---sanatate', 'petrol---gaze', 'prestari-servicii', 'manufactura',
                      'publicitate---marketing---pr', 'transport---logistica---import---export', 'turism---horeca']

list_of_types = ['Full time', 'Part time', 'Internship / Voluntariat', 'Proiect / Sezonier']



# Temporary hardcoding of counties

number_of_jobs = []
for county in list_of_counties:
    something = mycol.count_documents({"county": county})
    number_of_jobs.append(something)

data_temp = {"Counties": list_of_counties, "Number_of_jobs" : number_of_jobs}


for industry in list_of_industries:
    temp_numbers = []
    for county in list_of_counties:
        temp_numbers.append(mycol.count_documents({"county": county, "industry": industry}))
    data_temp[industry] = temp_numbers


for job_type in list_of_types:
    temp_types = []
    for county in list_of_counties:
        temp_types.append(mycol.count_documents({"county": county, "type": job_type}))
    data_temp[job_type] = temp_types


#data = mycol.find({}, {"_id": 0, "keywords": 0, "city": 0, "link": 0, "job_description": 0})

#dataframe = pd.DataFrame(data)

with urlopen(
        'https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/romania.geojson') as response:
    counties = json.load(response)

#print(f"Counties: {len(list_of_counties)} \nJobs: {len(number_of_jobs)} \nIndustries: {len(number_of_jobs_with_industries)} \nTypes: {len(number_of_jobs_with_types)}")

column_names = []
for col in data_temp:
    column_names.append(col)
column_names.pop(0)
print(column_names)

df = pd.DataFrame.from_dict(data_temp)

visible = np.array(column_names)

traces = []
buttons = []
for value in column_names:
    traces.append(go.Choropleth(featureidkey='properties.name', geojson=counties, locations=df['Counties'], z=df[value].astype(float), colorbar_title=value, visible=True if value==column_names[0] else False))

    buttons.append(dict(label=value, method="update", args=[{"visible":list(visible==value)},{"title":f"<b>{value}</b>"}]))

updatemenus = [{"active":0, "buttons":buttons}]


fig = go.Figure(data=traces, layout=dict(updatemenus=updatemenus))

first_title = [column_names[0]]
fig.update_layout(title=f"<b>{first_title}</b>", title_x=0.5)
fig.update_geos(fitbounds="locations", visible=True, scope="europe", showcountries=False)
fig.write_html(file="jobs_choropleth.html", include_plotlyjs="cdn", full_html=False)
#fig.show()

#fig = px.choropleth(df, geojson=counties, locations="Counties", scope="europe", color="alimentara",
#                        color_continuous_scale="Thermal",
#                        featureidkey='properties.name')
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#fig.update_geos(fitbounds="locations", visible=True)
#fig.update_geos(
#    visible=True, resolution=110, scope="europe",
#    showcountries=False, countrycolor="Black",
#    showsubunits=False, subunitcolor="Blue",
#    fitbounds="geojson"
#)
#fig.show()