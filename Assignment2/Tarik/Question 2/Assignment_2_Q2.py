import pandas as pd
import numpy as np
import os
from pathlib import Path


def load_temperature_data(data_dir):
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, data_dir)
    
    csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
    
    dfs = []
    for file in csv_files:
        file_path = os.path.join(data_path, file)
        df = pd.read_csv(file_path)
        year = file.split('.')[0][-4:]  # Gets last 4 characters before .csv
        df['STATION_NAME'] = df['STATION_NAME'] + '-' + year
        dfs.append(df)
    
    combined_data = pd.concat(dfs, ignore_index=True)
    
    # Delete first 4 columns except station names and store in refined_data
    refined_data = combined_data.iloc[:, [0] + list(range(4, combined_data.shape[1]))]

    
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3,
        'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9,
        'October': 10, 'November': 11, 'December': 12
    }
    
    refined_data.rename(columns=month_mapping, inplace=True)
    return refined_data

def calculate_seasonal_averages(df):
    season_mapping = {
        12: 'Summer', 1: 'Summer', 2: 'Summer',
        3: 'Autumn', 4: 'Autumn', 5: 'Autumn',
        6: 'Winter', 7: 'Winter', 8: 'Winter',
        9: 'Spring', 10: 'Spring', 11: 'Spring'
    }
    
    melted_df = df.melt(var_name='Month', value_name='Temperature')

    melted_df['Season'] = melted_df['Month'].map(season_mapping)
    
    seasonal_avg = melted_df.groupby('Season')['Temperature'].mean()
    return seasonal_avg

def find_largest_temp_range_stations(df):
    # Reset index to keep the station names
    df = df.reset_index()
    
    melted_df = df.melt(id_vars=['STATION_NAME'], var_name='Month', value_name='Temperature')
    
    # Group by station to find temperature ranges
    ranges = melted_df.groupby('STATION_NAME')['Temperature'].agg(['min', 'max'])
    ranges['range'] = ranges['max'] - ranges['min']
    
    max_range = ranges['range'].max()
    return ranges[ranges['range'] == max_range].index.tolist()

def find_warmest_coolest_stations(df):

    melted_df = df.melt(id_vars=['STATION_NAME'], var_name='Month', value_name='Temperature')
    
    station_max_temps = melted_df.groupby('STATION_NAME')['Temperature'].max()
    station_min_temps = melted_df.groupby('STATION_NAME')['Temperature'].min()
    
    warmest_stations = station_max_temps[station_max_temps == station_max_temps.max()].index.tolist()
    coolest_stations = station_min_temps[station_min_temps == station_min_temps.min()].index.tolist()
    
    return warmest_stations, coolest_stations

# Load the temperature data
refined_data = load_temperature_data('temperature_data')


# Calculate and save seasonal averages
seasonal_averages = calculate_seasonal_averages(refined_data)
with open('average_temp.txt', 'w') as f:
    f.write("Average Temperatures by Season:\n")
    for season in ['Summer', 'Autumn', 'Winter', 'Spring']:
        if season in seasonal_averages:
            f.write(f"{season}: {seasonal_averages[season]:.1f}C\n")
        

# Find and save stations with largest temperature range
largest_range_stations = find_largest_temp_range_stations(refined_data)
with open('largest_temp_range_station.txt', 'w') as f:
    
    f.write("Stations with Largest Temperature Range:\n")
    melted_df = refined_data.melt(id_vars=['STATION_NAME'], var_name='Month', value_name='Temperature')
    station_temps = melted_df.groupby('STATION_NAME')['Temperature'].agg(['min', 'max'])
    
    for station in largest_range_stations:
        min_temp = station_temps.loc[station, 'min']
        max_temp = station_temps.loc[station, 'max']
        temp_range = max_temp - min_temp
        
        f.write(f"{station}\n")
        f.write(f"Minimum Temperature: {min_temp:.1f}C\n")
        f.write(f"Maximum Temperature: {max_temp:.1f}C\n")
        f.write(f"Temperature Range: {temp_range:.1f}C\n\n")

# Find and save warmest and coolest stations
warmest, coolest = find_warmest_coolest_stations(refined_data)
with open('warmest_and_coolest_station.txt', 'w') as f:

    melted_df = refined_data.melt(id_vars=['STATION_NAME'], var_name='Month', value_name='Temperature')
    station_max_temps = melted_df.groupby('STATION_NAME')['Temperature'].max()
    station_min_temps = melted_df.groupby('STATION_NAME')['Temperature'].min()
    
    f.write("Warmest Stations:\n")
    for station in warmest:
        max_temp = station_max_temps[station]
        f.write(f"{station}: {max_temp:.1f}C\n")
    
    f.write("\nCoolest Stations:\n")
    for station in coolest:
        min_temp = station_min_temps[station]
        f.write(f"{station}: {min_temp:.1f}C\n")


