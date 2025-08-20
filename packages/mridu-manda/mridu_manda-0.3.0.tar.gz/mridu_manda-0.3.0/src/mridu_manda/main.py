import requests
import json
import os
from mridu_manda import setup_mridumanda


def main():
    setup_mridumanda.setup()
    
    print("Welcome to MriduManda")
    city = input("Enter city name: ")
    path_to_api = os.path.join(os.path.expanduser("~"), ".mridumanda", "api.txt")
    api = None
    
    with open (path_to_api, "r") as file:
        line = file.readline()
        
        if ":" in line:
            key, value = line.strip().split(":", 1)
            api = value
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric"
    response = requests.get(url)
    
    os.system('clear')
    
    if response.status_code == 200:
        weather_data = response.json()
        print(f"Weather in {city.title()}: {weather_data['weather'][0]['description']}")
        print(f"Temperature: {weather_data['main']['temp']}°C")
    else:
        print("Error:", response.status_code)
