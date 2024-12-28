import pandas as pd
from geopy.distance import geodesic


def validate_coordinates(coord):
    try:
        lat, lng = map(float, coord)
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except ValueError:
        return False


def DistanceCalculator(origin, destination):
    return geodesic(origin, destination).kilometers


def locationCoordinatesExtractor(locationUrl):
    coordinates = None
    if '/@' in locationUrl:
        first_split = locationUrl.split('/@')
        coordinates = first_split[1].split(',')[0:2]
    else:
        coordinates = locationUrl.split(',')
    if coordinates and validate_coordinates(coordinates):
        coordinates = tuple(map(float, coordinates))
        return coordinates

    return None


final_data = []
centers_df = pd.read_excel('centers.xlsx')  # Replace with your file path
stations_df = pd.read_excel('stations.xlsx')

for _, center in centers_df.iterrows():
    center_id = center['id']
    if pd.notna(center['location']):
        
        center_coords = locationCoordinatesExtractor(center['location'])
        print(center_coords)
        if center_coords:
        

            for _, station in stations_df.iterrows():
                station_topic = station['topic']  # E.g., 'metro' or 'brt'
                station_name = station['name']
                station_coords = (station['POINT_Y'], station['POINT_X'])
                distance = DistanceCalculator(center_coords, station_coords)
            
                
                location_url = f"https://www.google.com/maps?q={station_coords[0]},{station_coords[1]}"

                final_data.append({
                    'center': center_id,
                    'topic': station_topic,
                    'name': station_name,
                    'coordinates': f"{station_coords[0]},{station_coords[1]}",
                    'location': location_url,
                    'distance': round(distance, 2)
                })

# Create a DataFrame with all the data
final_df = pd.DataFrame(final_data)

# Extract the two nearest stations for each topic for each center
nearest_stations = (
    final_df
    .sort_values(by=['center', 'topic', 'distance'])  # Sort by center, topic, and distance
    .groupby(['center', 'topic'])  # Group by center and topic
    .head(2)  # Take the top 2 nearest stations for each center-topic group
)
nearest_stations['topic'] = (
    nearest_stations
    .groupby(['center', 'topic'])
    .cumcount()  # Count the station index within each group
    .add(1)  # Start numbering from 1
    .astype(str)  # Convert to string
    .radd(nearest_stations['topic'] + ' ')  # Add "metro " or "brt " prefix
)
# Save the filtered data to a new Excel file
nearest_stations.to_excel('output_nearest_stations2.xlsx', index=False)

print("Data saved to output_nearest_stations.xlsx")
