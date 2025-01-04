# # Question2:
import os
import csv
from collections import defaultdict

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
seasons = {
        'Summer': ['December', 'January', 'February'],
        'Autumn': ['March', 'April', 'May'],
        'Winter': ['June', 'July', 'August'],
        'Spring': ['September', 'October', 'November']
    }

def seasonal_average_result(files, months):
    
    seasonal_arr = {season: [] for season in seasons}
    
    for row in files:
        # Skip first 4 columns (STATION_NAME, STN_ID, LAT, LON)
        temparatures = row[4:]
        for i, temp in enumerate(temparatures):
            month = months[i]
            for season, month_of_season in seasons.items():
                if month in month_of_season:
                    seasonal_arr[season].append(float(temp))
    
    # Calculate the average temperature for each season
    seasonal_average = {season: sum(temparatures)/len(temparatures) for season, temparatures in seasonal_arr.items()}
    
    return seasonal_average

def the_largest_range_station(files):
    range_of_temperature = {}
    for row in files:
        station = row[0]  
        temparatures = row[4:]
        temperature_range = float(max(temparatures)) - float(min(temparatures))
        range_of_temperature[station] = float(temperature_range)

    the_largest_range_station = max(range_of_temperature)
    
    return the_largest_range_station, range_of_temperature[the_largest_range_station]

def the_warmest_and_coolest_stations(files):
    avg_temperature_of_stations = {}
    for row in files:
        station = row[0]  
        temparatures = row[4:]
        temparatures = [float(temp) for temp in temparatures]
        avg_temperature_of_stations[station] = float(sum(temparatures)) / len(temparatures)
        

    the_warmest_station = max(avg_temperature_of_stations)
    the_coolest_station = min(avg_temperature_of_stations)
    
    return the_warmest_station, avg_temperature_of_stations[the_warmest_station], the_coolest_station, avg_temperature_of_stations[the_coolest_station]

def process_temperature_data(directory):
    temperature_data = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            with open(os.path.join(directory, filename), 'r') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    temperature_data.append(row)
    
    return temperature_data

def main():
    directory = 'temperature_data'  # Folder containing all the CSV files
    folder = process_temperature_data(directory)
    
    # Task 1: Calculate monthly average temperature
    seasonal_avg = seasonal_average_result(folder, months)
    with open('average_temp.txt', 'w', encoding="utf-8") as file:
        file.write('Average temperature for each season:\n')
        for season, avg_temp in seasonal_avg.items():
            file.write(f'{season}: {avg_temp:.2f}\n')
    the_largest_range_station_name, the_largest_range = the_largest_range_station(folder)
    with open('largest_temp_range_station.txt', 'w', encoding="utf-8") as file:
        file.write(f'The largest temperature range station is {the_largest_range_station_name} at {the_largest_range:.2f}')
    the_warmest_station, the_warmest_value, the_coolest_station, the_coolest_value = the_warmest_and_coolest_stations(folder)
    with open('warmest_and_coolest_station.txt', 'w', encoding="utf-8") as file:
        file.write(f'The warmest station is {the_warmest_station} at {the_warmest_value:.2f} \nThe coolest station is {the_coolest_station} at {the_coolest_value:.2f}')



main()

