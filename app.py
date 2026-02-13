import streamlit as st
import requests
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim

# --- [설정] 날씨 API 키만 넣으세요 ---
WEATHER_API_KEY = "c8d1af88d4fa4db68020fa92400179b6"

st.set_page_config(page_title="프리 트래블 가이드", layout="wide")
st.title("🌍 구글 없이 즐기는 실시간 여행 가이드")

# Nominatim 설정 (무료 주소 검색 서비스)
geolocator = Nominatim(user_agent="my_travel_app_2026")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ 지도를 클릭하거나 위치를 검색하세요")
    search_query = st.text_input("목적지 검색", placeholder="예: 파리 에펠탑, 서울역")
    
    # 기본 위치 (서울)
    start_coords = [37.5665, 126.9780]
    
    if search_query:
        location = geolocator.geocode(search_query)
        if location:
            start_coords = [location.latitude, location.longitude]
    
    m = folium.Map(location=start_coords, zoom_start=15)
    m.add_child(folium.LatLngPopup())

    # [Overpass API] 주변 식당 정보 가져오기 (무료)
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    node["amenity"="restaurant"](around:1000, {start_coords[0]}, {start_coords[1]});
    out;
    """
    try:
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()
        for element in data['elements'][:15]:
            lat, lon = element['lat'], element['lon']
            name = element.get('tags', {}).get('name', '식당')
            folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='green', icon='info-sign')).add_to(m)
    except:
        pass

    map_data = st_folium(m, width=800, height=500)

# 클릭 정보 처리
clicked_lat, clicked_lon = None, None
if map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lon = map_data["last_clicked"]["lng"]

with col2:
    st.subheader("ℹ️ 실시간 정보")
    if clicked_lat and clicked_lon:
        # 날씨 정보 (OpenWeather)
        w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={clicked_lat}&lon={clicked_lon}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
        w_res = requests.get(w_url).json()
        
        st.info(f"📍 선택된 위치: {w_res.get('name', '좌표 지정 구역')}")
        st.metric("현재 온도", f"{w_res['main']['temp']}°C", w_res['weather'][0]['description'])
        
        # 이동 경로 링크 (구글 앱 대신 웹용 구글맵으로 바로 연결)
        map_link = f"https://www.google.com/maps/dir/?api=1&destination={clicked_lat},{clicked_lon}"
        st.markdown(f"[🔗 이곳으로 가는 길 찾기 (구글맵 연결)]({map_link})")
    else:
        st.write("지도에서 원하는 곳을 클릭해 보세요.")