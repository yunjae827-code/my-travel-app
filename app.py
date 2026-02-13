import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- [1] 페이지 설정 ---
st.set_page_config(page_title="스마트 경로 가이드", layout="wide")

# 다크/라이트 모드 대응 CSS
st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 데이터 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6"
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    return requests.get(url).json()

# --- [3] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 2.5])

# 세션 상태 초기화
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 37.5547, 126.9707 # 서울역
    st.session_state.addr = "서울역"

with col_info:
    st.markdown("### 🗺️ 경로 및 날씨 가이드")
    
    # 출발지는 현위치로 자동 안내
    st.write("📍 **출발:** 현위치 (브라우저 GPS)")
    
    # 목적지 검색
    dest_input = st.text_input("🚩 목적지 입력", placeholder="예: 강남역, 해운대...")
    if dest_input:
        geolocator = Nominatim(user_agent="my_travel_v8")
        loc = geolocator.geocode(dest_input)
        if loc:
            st.session_state.lat, st.session_state.lon, st.session_state.addr = loc.latitude, loc.longitude, dest_input

    # 날씨 정보
    try:
        w = get_weather(st.session_state.lat, st.session_state.lon)
        st.markdown(f"""
            <div class="weather-card">
                <h4>🌤️ {st.session_state.addr} 날씨</h4>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p>{w['weather'][0]['description']}</p>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.warning("날씨 API 키를 확인해주세요.")

    # 교통 정보 (내부 팝업 형태)
    st.markdown("### 🚌 교통 정보")
    g_link = f"https://www.google.com/maps/dir/My+Location/{st.session_state.lat},{st.session_state.lon}/"
    st.markdown(f'<a href="{g_link}" target="_blank"><button style="width:100%; padding:10px; cursor:pointer;">🚇 실시간 경로 상세 보기 (새창)</button></a>', unsafe_allow_html=True)
    st.info("지도에서 역이나 장소를 직접 클릭하면 정보가 업데이트됩니다.")

with col_map:
    # [핵심] 휠 스크롤이 즉시 가능하고 클릭이 되는 인터랙티브 지도
    # 한국어 지명이 잘 보이는 OpenStreetMap 활용
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=15)
    
    # 클릭 시 좌표를 가져오는 기능 추가
    m.add_child(folium.LatLngPopup())
    
    # 현재 목적지에 마커 표시
    folium.Marker(
        [st.session_state.lat, st.session_state.lon], 
        popup=st.session_state.addr,
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # 지도를 화면에 표시 (휠 스크롤 즉시 허용 설정 포함)
    map_data = st_folium(m, width="100%", height=800)

    # 지도 클릭 시 세션 상태 업데이트 (역 클릭 효과)
    if map_data.get("last_clicked"):
        st.session_state.lat = map_data["last_clicked"]["lat"]
        st.session_state.lon = map_data["last_clicked"]["lng"]
        st.session_state.addr = "선택된 지점"
        st.rerun()
