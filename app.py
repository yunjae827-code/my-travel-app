import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- [설정] 페이지 레이아웃 및 스타일 ---
st.set_page_config(page_title="스마트 트래블 가이드", layout="wide", initial_sidebar_state="collapsed")

# 네이버 지도 스타일의 UI 구현을 위한 CSS
st.markdown("""
    <style>
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; }
    .stApp { background-color: white; }
    /* 정보창 스타일 */
    .info-panel { background-color: #f8f9fa; border-right: 1px solid #ddd; height: 100vh; padding: 20px; overflow-y: auto; }
    .weather-card { background-color: #e3f2fd; border-radius: 10px; padding: 15px; margin-bottom: 20px; border-left: 5px solid #2196f3; }
    .transport-option { border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: white; }
    .time-badge { background-color: #00c73c; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- [함수] 데이터 가져오기 ---
def get_weather_data(lat, lon, lang_code):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 여기에 본인 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang={lang_code}"
    return requests.get(url).json()

# --- [메인 레이아웃] ---
col_info, col_map = st.columns([1, 2.5])

# 초기 좌표 (서울역)
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 37.5547, 126.9707
    st.session_state.addr = "서울역"

with col_info:
    st.markdown("### 🔍 장소 검색")
    lang = st.radio("Language", ["한국어", "English"], horizontal=True, label_visibility="collapsed")
    lang_code = 'kr' if lang == "한국어" else "en"
    
    search_q = st.text_input("목적지 입력" if lang == "한국어" else "Enter destination", placeholder="예: 서울역, 강남역...")
    
    if search_q:
        geolocator = Nominatim(user_agent="my_geo_app")
        loc = geolocator.geocode(search_q)
        if loc:
            st.session_state.lat, st.session_state.lon, st.session_state.addr = loc.latitude, loc.longitude, search_q

    # 날씨 정보 섹션
    try:
        w = get_weather_data(st.session_state.lat, st.session_state.lon, lang_code)
        st.markdown(f"""
            <div class="weather-card">
                <h4>🌤️ {st.session_state.addr} {'날씨' if lang == '한국어' else 'Weather'}</h4>
                <h2 style="margin:0;">{w['main']['temp']}°C</h2>
                <p style="margin:0; color:#555;">{w['weather'][0]['description']} | {'습도' if lang == '한국어' else 'Hum'}: {w['main']['humidity']}%</p>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.error("날씨 정보를 불러올 수 없습니다.")

    # 교통 정보 섹션 (네이버 지도 느낌 구현)
    st.markdown("### 🚌 교통 수단별 상황")
    
    # 구글맵 실시간 경로 링크 생성
    g_link = f"https://www.google.com/maps/dir/Current+Location/{st.session_state.lat},{st.session_state.lon}"
    
    st.markdown(f"""
        <div class="transport-option">
            <span class="time-badge">최적</span> <b>지하철/버스</b>
            <p style="font-size:0.9em; color:#666; margin-top:5px;">실시간 배차 및 환승 정보 확인</p>
            <a href="{g_link}/data=!4m2!4m1!3e3" target="_blank"><button style="width:100%; cursor:pointer;">경로 상세 보기</button></a>
        </div>
        <div class="transport-option">
            <b>🚕 택시 / 자차</b>
            <p style="font-size:0.9em; color:#666; margin-top:5px;">교통 체증 반영 예상 시간 확인</p>
            <a href="{g_link}/data=!4m2!4m1!3e0" target="_blank"><button style="width:100%; cursor:pointer;">실시간 내비 연결</button></a>
        </div>
    """, unsafe_allow_html=True)

with col_map:
    # 지도 표시 (어두워지지 않는 OpenStreetMap 타일)
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=15, tiles="OpenStreetMap")
    
    # 현위치 추적 버튼
    folium.plugins.LocateControl(auto_start=False).add_to(m)
    
    # 목적지 마커
    folium.Marker(
        [st.session_state.lat, st.session_state.lon],
        popup=st.session_state.addr,
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # 지도를 클릭해서 위치 변경 가능하게 설정
    map_res = st_folium(m, width="100%", height=800, use_container_width=True)
    
    if map_res.get("last_clicked"):
        st.session_state.lat = map_res["last_clicked"]["lat"]
        st.session_state.lon = map_res["last_clicked"]["lng"]
        st.session_state.addr = "선택한 위치" if lang == "한국어" else "Selected point"

        st.rerun()
