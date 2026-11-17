import requests
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: ("Sunny / Clear", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Cloudy", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "🌨️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}

@st.cache_data(ttl=600, show_spinner=False)
def find_places(query: str):
    response = requests.get(
        GEOCODING_URL,
        params={"name": query, "count": 10, "language": "en", "format": "json"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get("results", [])

@st.cache_data(ttl=600, show_spinner=False)
def get_weather(latitude: float, longitude: float, timezone: str):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m", "apparent_temperature", "relative_humidity_2m",
            "is_day", "precipitation", "weather_code", "wind_speed_10m"
        ],
        "daily": [
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "precipitation_probability_max"
        ],
        "forecast_days": 5,
        "timezone": timezone or "auto",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
    }
    response = requests.get(FORECAST_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()

def weather_label(code):
    return WEATHER_CODES.get(code, ("Weather conditions unavailable", "🌡️"))

st.set_page_config(page_title="WeatherNow", page_icon="🌦️", layout="centered")
st.markdown("""
<style>
    .stApp {background: linear-gradient(145deg, #0b1d36 0%, #123b5d 55%, #176b78 100%);}
    h1, h2, h3, p, label, .stMarkdown {color: #f4f8ff;}
    .weather-card {
        background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.2);
        border-radius: 18px; padding: 22px; margin: 10px 0;
        box-shadow: 0 8px 28px rgba(0,0,0,.12);
    }
    .big-temp {font-size: 3.5rem; font-weight: 750; line-height: 1.1;}
    .muted {color: #d5e5f2; font-size: .95rem;}
    [data-testid="stMetric"] {background: rgba(255,255,255,.12); padding: 14px; border-radius: 14px;}
</style>
""", unsafe_allow_html=True)

st.title("🌦️ WeatherNow")
st.caption("Current conditions and a 5-day forecast for cities and regions around the world.")

query = st.text_input("Search for a city or state", placeholder="e.g. Jaipur, Maharashtra, London")
if st.button("Find location", type="primary", use_container_width=True):
    if query.strip():
        try:
            st.session_state["places"] = find_places(query.strip())
            st.session_state["searched_query"] = query.strip()
        except requests.RequestException:
            st.error("Could not reach the location service. Check your internet connection and try again.")
    else:
        st.warning("Enter a city or state name first.")

places = st.session_state.get("places", [])
if places:
    labels = [
        f'{p["name"]}, {p.get("admin1", "") + ", " if p.get("admin1") else ""}{p.get("country", "")}'
        for p in places
    ]
    selected_index = st.selectbox(
        "Choose the correct location",
        options=range(len(places)),
        format_func=lambda i: labels[i],
    )
    selected = places[selected_index]

    if st.button("Show weather", use_container_width=True):
        st.session_state["selected_place"] = selected

place = st.session_state.get("selected_place")
if place:
    st.divider()
    place_name = place["name"]
    region = place.get("admin1", "")
    country = place.get("country", "")
    st.subheader(f"Weather in {place_name}")
    st.caption(", ".join(x for x in [region, country] if x))

    try:
        with st.spinner("Getting the latest weather..."):
            data = get_weather(place["latitude"], place["longitude"], place.get("timezone", "auto"))
        current = data["current"]
        description, emoji = weather_label(current["weather_code"])

        st.markdown(f"""
        <div class="weather-card">
            <div style="font-size:3rem">{emoji}</div>
            <div class="big-temp">{current["temperature_2m"]:.1f}°C</div>
            <div style="font-size:1.25rem;font-weight:600">{description}</div>
            <div class="muted">Feels like {current["apparent_temperature"]:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Humidity", f'{current["relative_humidity_2m"]}%')
        c2.metric("Wind", f'{current["wind_speed_10m"]} km/h')
        c3.metric("Precipitation", f'{current["precipitation"]} mm')

        st.subheader("5-day forecast")
        daily = data["daily"]
        cols = st.columns(5)
        for i, col in enumerate(cols):
            day = datetime.fromisoformat(daily["time"][i]).strftime("%a")
            desc, icon = weather_label(daily["weather_code"][i])
            rain = daily["precipitation_probability_max"][i]
            with col:
                st.markdown(f"""
                <div class="weather-card" style="text-align:center;padding:12px 5px">
                    <b>{day}</b><br><span style="font-size:1.8rem">{icon}</span><br>
                    <b>{daily["temperature_2m_max"][i]:.0f}°</b> /
                    {daily["temperature_2m_min"][i]:.0f}°<br>
                    <span class="muted" style="font-size:.8rem">{rain if rain is not None else "—"}% rain</span>
                </div>
                """, unsafe_allow_html=True)
        st.caption(f'Last updated: {current["time"].replace("T", " ")} (local time)')
    except (requests.RequestException, KeyError, ValueError) as exc:
        st.error("Weather data could not be loaded. Please try again in a moment.")
        st.caption("Check your internet connection. The free weather service may also be temporarily unavailable.")

st.divider()
st.caption("Weather data: Open-Meteo. Internet connection required. Temperatures are shown in °C.")
