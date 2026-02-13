import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- [1] 페이지 및 스타일 ---
st.set_page_config(page_title="프리 트래블 가이드", layout="wide")

st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    .transport-info {
        background-color: rgba(0, 199, 60, 0.1);
        border-radius: 10px; padding: 15px; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 세션 상태 초기화 ---
if 'start_loc' not in st.session_state:
    st.session_state.start_loc = {"lat": 37.5665, "lon": 126.9780, "addr": "서울시청"}
if 'dest_loc' not in st.session_state:
    st.session_state.dest_loc = {"lat": 37.5547, "lon": 126.9707, "addr": "서울역"}
if 'route_data' not in st.session_state:
    st.session_state.route_data = None

# --- [3] 날씨 및 경로 계산 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 본인의 날씨 키만 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try: return requests.get(url).json()
    except: return None

def get_route(start, end):
    # API 키 없이 경로 좌표를 가져오는 무료 OSRM 엔진
    url = f"http://router.project-osrm.org/route/v1/driving/{start['lon']},{start['lat']};{end['lon']},{end['end_lat']}?overview=full&geometries=geojson"
    try: return requests.get(url).json()
    except: return None

# --- [4] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 3])

with col_info:
    st.markdown("### 🔍 경로 설정")
    start_q = st.text_input("📍 출발 지점", value=st.session_state.start_loc['addr'])
    dest_q = st.text_input("🚩 도착 지점", value=st.session_state.dest_loc['addr'])
    
    if st.button("경로 계산 및 정보 업데이트"):
        geolocator = Nominatim(user_agent="my_travel_v13")
        loc_s = geolocator.geocode(start_q)
        loc_d = geolocator.geocode(dest_q)
        if loc_s and loc_d:
            st.session_state.start_loc = {"lat": loc_s.latitude, "lon": loc_s.longitude, "addr": start_q}
            st.session_state.dest_loc = {"lat": loc_d.latitude, "lon": loc_d.longitude, "addr": dest_q}
            st.rerun()

    # 날씨 정보
    w = get_weather(st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon'])
    if w and 'main' in w:
        st.markdown(f"""<div class="weather-card">
            <h4>🌤️ 도착지 날씨: {w['main']['temp']}°C</h4>
            <p>{w['weather'][0]['description']}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 🚌 교통 안내")
    st.markdown(f"""<div class="transport-info">
        <b>현위치 기준 추천 경로</b><br>
        • 최적 경로 정보가 지도 위에 표시됩니다.<br>
        • 상세 시간은 교통 상황에 따라 변동됩니다.
    </div>""", unsafe_allow_html=True)

with col_map:
    # 한글 지명이 지원되는 지도 생성
    m = folium.Map(
        location=[st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], 
        zoom_start=14,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=ko", 
        attr="Google Maps (Korean)"
    )
    
    # 지도에 출발/도착 마커 및 경로 선 그리기
    folium.Marker([st.session_state.start_loc['lat'], st.session_state.start_loc['lon']], 
                  popup="출발", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker([st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], 
                  popup="도착", icon=folium.Icon(color='red')).add_to(m)
    
    # 두 지점을 연결하는 경로 선 (심플)
    folium.PolyLine(
        locations=[[st.session_state.start_loc['lat'], st.session_state.start_loc['lon']], 
                   [st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']]],
        color="blue", weight=5, opacity=0.7
    ).add_to(m)

    # 지도 렌더링 및 클릭 이벤트
    map_data = st_folium(m, width="100%", height=850, returned_objects=["last_clicked"])

    if map_data and map_data.get("last_clicked"):
        lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        st.write(f"📍 선택됨: {lat:.4f}, {lon:.4f}")
        c1, c2 = st.columns(2)
        if c1.button("출발지로"): 
            st.session_state.start_loc = {"lat": lat, "lon": lon, "addr": "지도 선택"}
            st.rerun()
        if c2.button("도착지로"): 
            st.session_state.dest_loc = {"lat": lat, "lon": lon, "addr": "지도 선택"}
            st.rerun()
