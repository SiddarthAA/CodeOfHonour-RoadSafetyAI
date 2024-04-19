import folium 
import csv

def Map():
    try:    
        fh = open("C:\\Users\\siddu\\Desktop\\Local\\Module-Z(Pothole)\\co-ords.csv","r")
        reader = csv.reader(fh)
        coordinates = list()

        for i in reader:
            coordinates.append(i)
        mymap = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
        for coord in coordinates:
            folium.Marker(location=coord).add_to(mymap)

        mymap.save("C:\\Users\\siddu\\Desktop\\Local\\Module-Z(Pothole)\\map.html")

    except:
        print("Not Working")

Map()