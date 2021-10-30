from flask import Flask, render_template  
                            
import folium
from folium.map import LayerControl
import pandas as pd
import io
import requests
from datetime import date
import datetime
 
fg = folium.FeatureGroup(name='Markers')        #creates Feature Group called Markers. This is a layer that can be switched of if necessary
pd.set_option('display.max_rows', 1000)         #not necessary, used to print whole column while testing
 
today = datetime.datetime.now()                     #get today date
yesterday = today - datetime.timedelta(days=1)      #get yesterday date
month_yes = str(int(yesterday.strftime("%m")))      # extracts month, transforms it into int and back to string. from 09 to 9 for september. Csv doc didn't have zeros in it's columns so I had to do that
date_yes = str(int(yesterday.strftime("%d")))       # same thing for date
year = yesterday.strftime("%y")                     #extracts year
date_fixed = f'{month_yes}/{date_yes}/{year}'       #creates new, formated date, ex. from 09/04/21 to 9/4/21
 
 #imports csv doc from url.
url = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_deaths_global.csv&filename=time_series_covid19_deaths_global.csv"
s = requests.get(url).content
#creates new dataframe with only three columns
data = pd.read_csv(io.StringIO(s.decode('utf-8')), usecols = ['Lat','Long', date_fixed])
 
 #drops indexes with NaN values
data_fixed = data.dropna(axis = 0)
 
#Geographic coordinate lists
lat = list(data_fixed['Lat'])        
lon = list(data_fixed['Long'])
 
#Death total list
death_total = list(data_fixed[date_fixed])
 
#https://datahub.io/core/geo-countries
#import of GeoJson doc

with open('countries.geojson', 'r+') as file:  #This section of code imports Json file, replaces 'ADMIN' with 'NAME' so I could get for ex. NAME SERBIA
    content = file.read()
    file.seek(0)
    fixed_json = content.replace('ADMIN', 'Country: ')    
 
#Creating a map
m = folium.Map(location =[44.0165, 21.0059],
  zoom_start=4,
  tiles='OpenStreetMap')
 
#function that will be used to define color of each marker
def color_chooser(x):
    if x <1000:
        return 'green'
    elif 1000 <= x <10000:
        return 'orange'
    elif 10000 <= x <50000:
        return 'red'
    elif 50000 <= x <=100000:
        return 'darkred'
    elif 100000 < x :
        return 'black'
    
 
#create Choroleth map with polygons based on countries.geojson doc
g = folium.GeoJson(fixed_json, name="Poligons").add_to(m)
folium.GeoJsonTooltip(fields=['Country: ']).add_to(g)               
 
#Create Markers using for loop and folium.Marker class
for la,lo,de in zip(lat, lon, death_total):
    fg.add_child(folium.Marker(location=[la, lo],popup=(f'Total death count until {date_fixed} is ' + str(de)) ,icon=folium.Icon(color=color_chooser(de))))
 
 
m.add_child(fg)
m.add_child(LayerControl())
m.save("templates/index.html")
app = Flask(__name__) 



@app.route('/')     #homepage

def home():         
    return render_template('index.html')         #places index.html from the templates folder on the homepage


if __name__ == '__main__':              
    app.run(debug=True)                 
