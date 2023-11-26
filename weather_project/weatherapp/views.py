from django.shortcuts import render
import requests
import datetime

def index(request):
    api_key = '<your API_KEY>'
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
    dates = set()
    for data in forecast_response['list']:
        date_txt = data['dt_txt']
        date_obj = datetime.datetime.strptime(date_txt, '%Y-%m-%d %H:%M:%S')
        date = date_obj.date()

        if date not in dates and date_obj.hour == 12:
            dates.add(date)

            min_temp = max_temp = data['main']['temp']
            for hour_data in forecast_response['list']:
                hour_date_txt = hour_data['dt_txt']
                hour_date_obj = datetime.datetime.strptime(hour_date_txt, '%Y-%m-%d %H:%M:%S')
                hour_date = hour_date_obj.date()
                
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

    return weather_data, daily_forecasts[:5]

