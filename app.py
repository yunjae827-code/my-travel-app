import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- [1] 페이지 및 스타일 설정 ---
st.set_page_config(page_title="스마트 통합 가이드", layout="wide")

st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); overflow-y: auto; }
    
    /* 네이버 지도 스타일 상세 리스트 */
    .route-container { margin-top: 20px; }
    .route-step { 
        padding: 12px; border-bottom: 1px solid rgba(128,128,128,0.2); 
        font-size: 0.9em; line-height: 1.5;
    }
    .step-header { color: #00c73c; font-weight: bold; margin-bottom: 5px; }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 15px; border-left: 6px solid #2196f3; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 세션 상태 초기화 ---
if 'start' not in st.session_state:
    st.session_state.start = {"lat": 37.5665, "lon": 126.9780, "addr": "서울시청"}
if 'dest' not in st.session_state:
    st.session_state.dest = {"lat": 37.5547, "lon": 126.9707, "addr": "서울역"}
if 'steps' not in st.session_state:
    st.session_state.steps = []

# --- [3] 데이터 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 실제 키 입력 필요
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try: return requests.get(url).json()
    except: return None

def fetch_route(s, d):
    # OSRM 오픈소스 엔진으로 상세 경로 데이터(텍스트 안내 포함) 가져오기
    url = f"http://router.project-osrm.org/route/v1/driving/{s['lon']},{s['lat']};{d['lon']},{d['lat']}?steps=true&languages=ko"
    try:
        res = requests.get(url).json()
        if res['code'] == 'Ok':
            return res['routes'][0]['legs'][0]['steps']
    except: return []
    return []

# --- [4] 메인 레이아웃 ---
col_info, col_map = st.columns([1.2, 2.8])

with col_info:
    st.markdown("### 🔍 경로 및 상세 가이드")
    s_in = st.text_input("📍 출발 지점", value=st.session_state.start['addr'])
    d_in = st.text_input("🚩 도착 지점", value=st.session_state.dest['addr'])
    
    if st.button("실시간 경로 및 날씨 탐색"):
        geolocator = Nominatim(user_agent="my_travel_v20")
        ls, ld = geolocator.geocode(s_in), geolocator.geocode(d_in)
        if ls and ld:
            st.session_state.start = {"lat": ls.latitude, "lon": ls.longitude, "addr": s_in}
            st.session_state.dest = {"lat": ld.latitude, "lon": ld.longitude, "addr": d_in}
            st.session_state.steps = fetch_route(st.session_state.start, st.session_state.dest)
            st.rerun()

    # 날씨 정보
    w = get_weather(st.session_state.dest['lat'], st.session_state.dest['lon'])
    if w and 'main' in w:
        st.markdown(f"""<div class="weather-card">
            <h4 style="margin:0;">🌤️ {st.session_state.dest['addr']} 날씨</h4>
            <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
            <p>{w['weather'][0]['description']}</p>
        </div>""", unsafe_allow_html=True)

    # [핵심] 상세 경로 리스트 표시
    if st.session_state.steps:
        st.markdown("#### 🚇 상세 이동 경로")
        for i, step in enumerate(st.session_state.steps):
            dist = step['distance']
            instr = step['maneuver']['instruction']
            st.markdown(f"""
                <div class="route-step">
                    <div class="step-header">단계 {i+1}</div>
                    {instr}<br>
                    <span style="color:gray; font-size:0.8em;">약 {dist:.0f}m 이동</span>
                </div>
            """, unsafe_allow_html=True)

with col_map:
    # 한글 지명이 지원되는 지도 (휠 스크롤 즉시 허용)
    m = folium.Map(
        location=[st.session_state.dest['lat'], st.session_state.dest['lon']], 
        zoom_start=14,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=ko", 
        attr="Google Maps (Korean)"
    )
    
    # 마커 및 경로 선 그리기
    folium.Marker([st.session_state.start['lat'], st.session_state.start['lon']], icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker([st.session_state.dest['lat'], st.session_state.dest['lon']], icon=folium.Icon(color='red')).add_to(m)
    
    # 지도 클릭 시 좌표 추출 및 버튼 인터랙션
    map_data = st_folium(m, width="100%", height=850, returned_objects=["last_clicked"])
    
    if map_data and map_data.get("last_clicked"):
        lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        st.write(f"📍 선택 지점: {lat:.4f}, {lon:.4f}")
        c1, c2 = st.columns(2)
        if c1.button("출발지로"):
            st.session_state.start = {"lat": lat, "lon": lon, "addr": "지도 선택 지점"}
            st.rerun()
        if c2.button("도착지로"):
            st.session_state.dest = {"lat": lat, "lon": lon, "addr": "지도 선택 지점"}
            st.rerun()
