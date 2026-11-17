# WeatherNow — Python Weather App

A small browser-based weather app built with Python and Streamlit.

## Features
- Search for a city, town, or state/region.
- Choose the matching location from search results.
- Shows current temperature and **feels-like temperature**.
- Describes conditions such as sunny, cloudy, rainy, snowy, or thunderstorm.
- Shows humidity, wind speed, precipitation, and a 5-day forecast.
- Uses Open-Meteo's free APIs; no API key is required.

## Requirements
- Python 3.9 or newer
- Internet connection

## Run on Windows
1. Extract the ZIP file.
2. Open the extracted `weather_app` folder.
3. In File Explorer's address bar, type `cmd` and press Enter.
4. Run:

   ```bash
   py -m pip install -r requirements.txt
   py -m streamlit run app.py
   ```

5. Your browser opens the app. If it does not, visit `http://localhost:8501`.

## Run on macOS or Linux

From this folder, run:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Then open `http://localhost:8501` if the browser does not open automatically.

## Use it on other machines
This project runs on Windows, macOS, and Linux as long as Python and the dependencies are installed. Each machine needs internet access to fetch weather data.

To let people use it from any device without installing Python, deploy the folder to a hosting service that supports Streamlit (for example, Streamlit Community Cloud). A locally running copy is only available on that computer unless you deliberately configure network access.

## Notes
- Weather information is provided by Open-Meteo and can be delayed or unavailable occasionally.
- Search results may include cities and administrative regions with similar names; select the correct result.
