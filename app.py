import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- [1] 페이지 설정 및 자동 테마 대응 ---
st.set_page_config(page_title="스마트 트래블 가이드", layout="wide", initial_sidebar_state="collapsed")

# 시스템 모드(다크/라이트)에 따라 글자색이 자동 변환되도록 CSS 설정
st.markdown("""
    <style>
    /* 시스템 테마에 따라 텍스트 색상 자동 조절 */
    :root { --text-color: inherit; --bg-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    
    /* 정보창 카드 스타일 */
    .info-panel { padding: 20px; height: 100vh; overflow-y: auto; border-right: 1px solid rgba(128,128,128,0.2); }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.1); 
        border-radius: 10px; padding: 15px; margin-bottom: 20px; 
        border-left: 5px solid #2196f3; 
    }
    .transport-option { 
        border: 1px solid rgba(128,128,128,0.3); 
        border-radius: 8px; padding: 15px; margin-bottom: 10px; 
    }
    .time-badge { background-color: #00c73c; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    
    /* 지도 밝기 최적화 */
    iframe { filter: contrast(1.1) brightness(1.0); }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 데이터 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6"
    # 지도 언어와 별개로 날씨 데이터는 한국어로 고정 출력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    return requests.get(url).json()

# --- [3] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 2.5])

# 세션 상태 초기화 (서울역 기본값)
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 37.5547, 126.9707
    st.session_state.addr = "서울역"

with col_info:
    st.markdown("### 🔍 목적지 정보")
    
    # 장소 검색
    search_q = st.text_input("장소 검색", placeholder="예: 서울역, 도쿄타워, 에펠탑...")
    
    if search_q:
        geolocator = Nominatim(user_agent="my_travel_app_v3")
        loc = geolocator.geocode(search_q)
        if loc:
            st.session_state.lat, st.session_state.lon, st.session_state.addr = loc.latitude, loc.longitude, search_q

    # 날씨 섹션
    try:
        w = get_weather(st.session_state.lat, st.session_state.lon)
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ {st.session_state.addr} 날씨</h4>
                <h2 style="margin:10px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">상태: {w['weather'][0]['description']} | 습도: {w['main']['humidity']}%</p>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.error("날세요 키를 확인해주세요.")

    # 교통 정보 섹션
    st.markdown("### 🚌 실시간 교통편")
    g_link = f"https://www.google.com/maps/dir/?api=1&destination={st.session_state.lat},{st.session_state.lon}"
    
    st.markdown(f"""
        <div class="transport-option">
            <span class="time-badge">추천</span> <b>대중교통 (지하철/버스)</b>
            <p style="font-size:0.85em; margin-top:5px;">현재 위치 기준 실시간 배차 확인</p>
            <a href="{g_link}&travelmode=transit" target="_blank"><button style="width:100%; border-radius:5px; border:1px solid #ddd; cursor:pointer; padding:5px;">경로 상세 보기</button></a>
        </div>
        <div class="transport-option">
            <b>🚕 택시 / 자동차</b>
            <p style="font-size:0.85em; margin-top:5px;">교통 체증 반영 예상 소요 시간</p>
            <a href="{g_link}&travelmode=driving" target="_blank"><button style="width:100%; border-radius:5px; border:1px solid #ddd; cursor:pointer; padding:5px;">내비게이션 연결</button></a>
        </div>
    """, unsafe_allow_html=True)

with col_map:
    # 한국어 지명이 표시되는 Google Maps 타일 주소 사용 (API 키 없이 웹 레이어 활용)
    # hl=ko 파라미터를 통해 전 세계 지도를 한국어로 강제 표시
    tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=ko"
    
    m = folium.Map(
        location=[st.session_state.lat, st.session_state.lon], 
        zoom_start=15, 
        tiles=tile_url, 
        attr='Google Maps'
    )
    
    # 현위치 추적 및 마커
    folium.plugins.LocateControl().add_to(m)
    folium.Marker(
        [st.session_state.lat, st.session_state.lon],
        popup=st.session_state.addr,
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)

    # 인터랙티브 지도 설정
    map_res = st_folium(m, width="100%", height=850, use_container_width=True)
    
    if map_res.get("last_clicked"):
        st.session_state.lat = map_res["last_clicked"]["lat"]
        st.session_state.lon = map_res["last_clicked"]["lng"]
        st.session_state.addr = "선택된 위치"
        st.rerun()