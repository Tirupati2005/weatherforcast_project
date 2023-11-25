# weatherforcast_project:-
#Project Details:
- Build a weather dashboard using Python and the Flask/Django web framework.
- Use an HTTP client (e.g., Requests) to fetch weather data from a public weather API (e.g., OpenWeatherMap, WeatherStack).
- Display the fetched weather data in a user-friendly web interface.
- The dashboard should include, at a minimum, the current temperature, weather condition, and a forecast for the next 5 days.
- Implement responsive design for the dashboard using HTML, CSS, and JavaScript.
- Host the dashboard using Flask/Django on a platform of your choice.
  
#setting up django_project:-
-Building a weather dashboard using Django involves several steps are fallows.
-Create a Django project(use 'django-admin startproject project_name' to create a new Django project)
-Create an app for weather(use 'python manage.py startapp app_name' to create an app within your project specifically for handling weather-related functionality)

#Libraries Used:
requests: Used to make HTTP requests to the OpenWeatherMap API.
datetime: Utilized for handling date and time-related operations.

#Code:-views.py file

def index(request):            #The index function handles both GET and POST requests..
    api_key = '6af560462ed37c5292774a063bf63ec6' # openweather API key used for authentication.
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}'

    if request.method == 'POST':
        city = request.POST['city1']

        weather_data, daily_forecasts = fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url)

        context = {
            'weather_data': weather_data,
            'daily_forecasts': daily_forecasts,
        }

        return render(request, 'weatherapp/index.html', context)
    else:
        return render(request, 'weatherapp/index.html')


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    current_response = requests.get(current_weather_url.format(city, api_key)).json()
    lat, lon = current_response['coord']['lat'], current_response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    weather_data = {
        'city': city,
        'temperature': round(current_response['main']['temp'] - 273.15, 2),
        'description': current_response['weather'][0]['description'],
        'icon': current_response['weather'][0]['icon'],
    }

    daily_forecasts = []
    dates = set()  # To keep track of unique dates for forecast aggregation
    for data in forecast_response['list']:
        date_txt = data['dt_txt']  # Get the date and time for the forecast
        date_obj = datetime.datetime.strptime(date_txt, '%Y-%m-%d %H:%M:%S')
        date = date_obj.date()

        # Filter data for a single forecast per day
        if date not in dates and date_obj.hour == 12:  # Assuming the API provides data for noon (12:00:00)
            dates.add(date)
            # Capture the minimum and maximum temperatures for the day
            min_temp = max_temp = data['main']['temp']  # Initialize with the current temperature
            for hour_data in forecast_response['list']:
                hour_date_txt = hour_data['dt_txt']
                hour_date_obj = datetime.datetime.strptime(hour_date_txt, '%Y-%m-%d %H:%M:%S')
                hour_date = hour_date_obj.date()
                
                # Check if the hour_data belongs to the same date as the current date and update min/max temps
                if hour_date == date and 'main' in hour_data:
                    min_temp = min(min_temp, hour_data['main']['temp'])
                    max_temp = max(max_temp, hour_data['main']['temp'])

            daily_forecasts.append({
                'day': date.strftime('%A'),
                'min_temp': round(min_temp - 273.15, 2),
                'max_temp': round(max_temp - 273.15, 2),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
            })

    return weather_data, daily_forecasts[:5]  # Return the forecasts for the next 5 days for one city
