import json
from datetime import datetime
import folium
from folium.plugins import Fullscreen, ScrollZoomToggler
import pandas as pd


def update_version():
    with open("version.json", "w") as f:
        data = {
            "last_updated": str(datetime.now()),
        }
        json.dump(data, f)


def get_encampment_data():
    path = "https://docs.google.com/spreadsheets/d/11ceyUZKH1SHHKUiLxqpX04BUOWi5vh_kOc1AIZCXflE/export?gid=0&format=csv"
    encampment_data = pd.read_csv(path)
    encampment_data = encampment_data.convert_dtypes()

    encampment_data["Latitude"] = pd.to_numeric(
        encampment_data["Latitude"], errors="coerce"
    )
    encampment_data["Longitude"] = pd.to_numeric(
        encampment_data["Longitude"], errors="coerce"
    )
    encampment_data["Location"] = (
        encampment_data["City"].str.strip()
        + ", "
        + encampment_data["State"].str.strip()
    )

    return encampment_data


def process_data():
    encampment_data = get_encampment_data()
    encampment_data = encampment_data.dropna(subset=["Latitude", "Longitude"])

    usa_coord = [37.0902, -95.7129]  # Latitude, Longitude coord in decimal degrees

    # Get the maximum and minimum latitude and longitude
    max_lat, min_lat = (
        encampment_data["Latitude"].max()+10,
        encampment_data["Latitude"].min()-10,
    )
    max_lon, min_lon = (
        encampment_data["Longitude"].max()+10,
        encampment_data["Longitude"].min()-10,
    )

    # Create USA map with folium wrapper around leaflet.js
    usa_map = folium.Map(
        location=usa_coord,
        max_bounds = True,
        zoom_start=3,
        max_zoom=12,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        # world_copy_jump=True # copies markers across the wrapped map
        tiles=folium.TileLayer(no_wrap=True) # prevent map from infinitely wrapping
        # scrollWheelZoom=False,
        # dragging=False,
    )
    folium.TileLayer("cartodbpositron").add_to(usa_map)

    encampment_icon = "images/tent.png"
    cap_icon = "images/cap.png"

    for _, row in encampment_data.iterrows():
        if pd.notna(row["Thumbnail Photo"]) and row["Thumbnail Photo"] is not None:
            photo_id = row["Thumbnail Photo"].split("d/")[-1].split("/")[0]
            image_url = f"https://drive.google.com/thumbnail?id={photo_id}&sz=w320"
        else:
            print(f"Warning: Image Path is None for row {row['University Name']}")
            image_url = "https://drive.google.com/thumbnail?id=1y7nBpt24WcKlb5qD1vtb0N2i1JxKVhw9&sz=w320"

        popup_html = f"""
            <!DOCTYPE html>
            <html>
            <h4 align="left" style="font-family:Calibri; color:red"><strong><u>{row['University Name']}</u><strong>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet"/>
            </h4>
            <h5 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa fa-map-marker"></i> Location: </strong> {row['Location']}
            </h5>
            <h5 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa-regular fa-calendar-days"></i> Start Date:</strong> {row['Encampment Start Date']}
            </h5>
            <h5 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa-solid fa-layer-group"></i> Status:</strong> {row['Status']}
            </h5>
            <h5 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa-solid fa-layer-group"></i> Category: </strong> {row['Category']}
            </h5>
            <h5 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa-solid fa-handcuffs"></i> Police Violence Status:</strong> {row['Police Violence Status']}
            </h5>
            <h5 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa-solid fa-handcuffs"></i> Number of Arrests:</strong> {row['Number of Arrests']}
            </h5>
            <img src="{image_url}" alt="Image" style="width:250px;height:200px;">
            """

        if pd.notna(row["Police Violence"]):
            popup_html += f"""
                <h6 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa-solid fa-video"></i> Videos:</strong>
                    <a href={row['Police Violence']} target="_blank">Police Violence</a>
                </h6>
            """

        if pd.notna(row["Video_1"]):
            popup_html += f"""
                <h6 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa-solid fa-video"></i> Videos:</strong>
                    <a href={row['Video_1']} target="_blank">Solidarity Actions Video 1</a>
                </h6>
            """

        if pd.notna(row["Video_2"]):
            popup_html += f"""
                <h6 align="left" style="font-family:Calibri; color:green"> <strong><i class="fa-solid fa-video"></i> Videos:</strong>
                    <a href={row['Video_2']} target="_blank">Solidarity Actions Video 2</a>
                </h6>
            """

        if pd.notna(row["Category"]) and row["Category"] == "Encampment":
            icon = folium.CustomIcon(encampment_icon, icon_size=(60, 60))
        else:
            icon = folium.CustomIcon(cap_icon, icon_size=(60, 60))
        popup = folium.Popup(popup_html, max_width=300)
        folium.vector_layers.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=popup,
            icon=icon,
            tooltip=str(row["University Name"]),
        ).add_to(usa_map)

    # Set the map's boundaries based on the maximum and minimum latitudes and longitudes
    # usa_map.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]], padding=(10, 10))

    # Button to turn scroll zoom on/off
    folium.plugins.ScrollZoomToggler().add_to(usa_map)
    
    # Button for fullscreen mode
    folium.plugins.Fullscreen(
        position="topright",
        title="Expand Map",
        title_cancel="Exit Map",
        force_separate_button=True,
        ).add_to(usa_map)

    # Define maximum and minimum bounds for the map
    # max_bounds = usa_map.get_bounds()
    # usa_map.max_bounds = max_bounds

    usa_map.save("encampments_map.html")
    update_version()


process_data()
