import requests
import json

directions_api = "https://api.openrouteservice.org/v2/directions/driving-car"
geocode_api = "https://api.openrouteservice.org/geocode/search?"
key = "5b3ce3597851110001cf6248e79cd2b81b3f4972a1bdc642619cc50a"

def geocode_address(address):
    url = f"{geocode_api}api_key={key}&text={address}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        if json_data["features"]:
            coords = json_data["features"][0]["geometry"]["coordinates"]
            print(f"Geocoded coordinates for '{address}': {coords}")
            if -90 <= coords[1] <= 90 and -180 <= coords[0] <= 180:
                return coords
            else:
                print(f"Invalid coordinates for {address}")
        else:
            print(f"No results found for {address}")
    else:
        print(f"Error {response.status_code}: {response.text}")
    return None

while True:
    orig = input("Starting Location: ")
    if orig.lower() in ["quit", "q"]:
        break
    dest = input("Destination: ")
    if dest.lower() in ["quit", "q"]:
        break

    orig_coords = geocode_address(orig)
    dest_coords = geocode_address(dest)

    if not orig_coords or not dest_coords:
        print("住所を取得できませんでした。再試行してください。\n")
        continue

    body = {
        "coordinates": [orig_coords, dest_coords]
    }

    headers = {
        "Authorization": key,
        "Content-Type": "application/json"
    }

    response = requests.post(directions_api, headers=headers, json=body)
    json_data = response.json()

    if response.status_code == 200:
        if 'routes' in json_data and json_data['routes']:
            route = json_data['routes'][0]
            if 'segments' in route and route['segments']:
                segment = route['segments'][0]
                print("\nAPI Status: 成功\n")
                print("=============================================")
                print(f"Directions from {orig} to {dest}")
                duration = segment.get('duration', 'N/A') / 60
                distance = segment.get('distance', 'N/A') / 1000
                print(f"所要時間: {duration:.2f} 分")
                print(f"距離: {distance:.2f} km")
                print("=============================================")

                if 'steps' in segment:
                    for step in segment['steps']:
                        instruction = step.get('instruction', 'N/A')
                        step_distance = step.get('distance', 'N/A')
                        print(f"{instruction} ({step_distance:.1f} m)")
                print("=============================================\n")
            else:
                print("セグメント情報がありません。")
        else:
            print("ルートが取得できませんでした。")
    else:
        print(f"エラー: {response.status_code} - {response.text}")
