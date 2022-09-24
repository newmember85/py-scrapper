import json
import os
import folium
import webbrowser
import time
from Instagram import create_tor_request as torrequest, InstagramSearch
from bs4 import BeautifulSoup
from datetime import *


def test_load():
    with open("test_result.json", "r", encoding="utf-8") as f:
        result = json.load(f)
    return result.get("data").get("edge_owner_to_timeline_media").get("edges")


# Returns Lat and Long from given Location ID
def get_location_lat_long(location_id):
    url = f"https://www.instagram.com/explore/locations/{location_id}/"

    r = torrequest(url=url)
    soup = BeautifulSoup(r.content, 'html.parser')
    geo = soup.select('meta')
    if len(geo) >= 14:
        lat = geo[12].attrs["content"]
        long = geo[13].attrs["content"]
        return lat, long
    else:
        return None, None


# Collects Location IDS from all Posts
def get_post_location(result):
    locations = []
    for post in result:
        location_dict = post.get("node").get("location")
        if location_dict is not None:
            locations.append({"post_id": post.get('node').get('id'), "location_id": location_dict.get("id"),
                              "location_coordinates": get_location_lat_long(location_dict.get("id")),
                              "location_name": location_dict.get("name"),
                              "taken_at_timestamp": post.get('node').get('taken_at_timestamp')})
    return locations


# Displays Coordinates in Map
def folium_world_map(locations, file_path):
    world_map = folium.Map()
    for values in locations:
        coordinates = values["location_coordinates"]
        location_name = values["location_name"]
        taken_at_timestamp = values["taken_at_timestamp"]
        if coordinates[0] is not None:
            folium.Marker(coordinates,
                          popup=f"Location:{coordinates}" + '<br>' + f'Name:{location_name}' + '<br>' + f'Date:{date.fromtimestamp(taken_at_timestamp).strftime("%d.%m.Y")}').add_to(
                world_map)
            world_map.save(f"./data/{file_path}/post_map.html")
            webbrowser.open(f"./data/{file_path}/post_map.html")


class PostVisualisation(InstagramSearch):

    def __init__(self, user_name):
        super().__init__(user_name)

    # Reads the User Information from the json File
    def access_user_info_file(self):
        [json_file] = [file for file in os.listdir(f'./data/{self.user_name}') if
                       file.startswith(f"{self.user_name}")] or ["None"]
        try:
            with open(f'./data/{self.user_name}/{json_file}', "r", encoding="utf-8") as f:
                result = json.load(f)
        except FileNotFoundError as e:
            print(e)

        posts = result.get("data").get("edge_owner_to_timeline_media").get("edges")
        return posts

    def save_user_post_geolocation_file(self, data):
        try:
            file_path = fr'./data/{self.user_name}/{self.user_name}-geolocation.json'
            # create file
            with open(file_path, 'w') as fp:
                json.dump(data, fp)
        except Exception as e:
            print(f'File already exists: {e}')

    def create_user_map(self):
        user_data = self.access_user_info_file()
        locations = get_post_location(user_data)
        self.save_user_post_geolocation_file(locations)

        with open(fr"./data/{self.user_name}/{self.user_name}-geolocation.json", "r", encoding="utf-8") as fr:
            r = json.load(fr)

        folium_world_map(r, file_path=self.user_name)


if __name__ == '__main__':
    # Returns from the Result all Locations

    user_visu = PostVisualisation("philipp_blanz")
    user_visu.create_user_map()
