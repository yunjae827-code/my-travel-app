import streamlit as st
import requests
from geopy.geocoders import Nominatim

# --- [1] 페이지 설정 및 스타일 ---
st.set_page_config(page_title="스마트 교통 & 날씨 가이드", layout="wide")

st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    
    /* 왼쪽 패널 스타일 */
    .info-panel { padding: 25px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); overflow-y: auto; }
    
    /* 날씨 카드 디자인 */
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    
    /* 우측 빈 공간 배경 처리 (깔끔한 UI용) */
    .map-placeholder { 
        height: 100vh; display: flex; align-items: center; justify-content: center; 
        background-color: rgba(0,0,0,0.02); color: #888; font-size: 1.2em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 날씨 함수 ---
def get_weather(lat, lon):
    # 실제 OpenWeatherMap API 키를 입력하세요.
    api_key = "c8d1af88d4fa4db68020fa92400179b6" 
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url).json()
        if res.get("main"): return res
    except: return None
    return None

# --- [3] 세션 상태 초기화 ---
if 'start_addr' not in st.session_state:
    st.session_state.start_addr = "서울시청"
if 'dest_addr' not in st.session_state:
    st.session_state.dest_addr = "서울역"
if 'dest_lat_lon' not in st.session_state:
    st.session_state.dest_lat_lon = (37.5547, 126.9707)

# --- [4] 메인 레이아웃 ---
col_info, col_empty = st.columns([1.5, 2.5]) # 정보창을 조금 더 넓게 설정

with col_info:
    st.markdown("## 🔍 통합 경로 설정")
    
    # 입력 및 검색 섹션
    s_input = st.text_input("📍 출발 지점", value=st.session_state.start_addr)
    d_input = st.text_input("🚩 도착 지점", value=st.session_state.dest_addr)
    
    if st.button("탐색 실행 및 정보 갱신"):
        geolocator = Nominatim(user_agent="my_travel_v22")
        loc = geolocator.geocode(d_input)
        if loc:
            st.session_state.dest_lat_lon = (loc.latitude, loc.longitude)
            st.session_state.dest_addr = d_input
        st.session_state.start_addr = s_input
        st.rerun()

    st.markdown("---")

    # [1] 날씨 정보 (상단 배치)
    w = get_weather(st.session_state.dest_lat_lon[0], st.session_state.dest_lat_lon[1])
    if w:
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ {st.session_state.dest_addr} 날씨</h4>
                <h2 style="margin:10px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']} | 습도 {w['main']['humidity']}%</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("날씨 API 키를 설정하면 기온이 표시됩니다.")

    # [2] 상세 경로 열기 버튼 (날씨 바로 밑으로 이동)
    st.markdown("### 🚇 상세 대중교통 정보")
    s_param = st.session_state.start_addr.replace(" ", "+")
    d_param = st.session_state.dest_addr.replace(" ", "+")
    
    # 실시간 버스/지하철 상세 정보 링크
    route_url = f"https://www.google.co.kr/maps/dir/{s_param}/{d_param}/data=!4m2!4m1!3e3?hl=ko"
    
    st.link_button("🚌 실시간 버스/지하철 상세 정보 열기", route_url, use_container_width=True)
    st.caption(f"💡 {st.session_state.start_addr} → {st.session_state.dest_addr} 경로의 소요 시간과 정류장 정보를 확인합니다.")

with col_empty:
    st.markdown("""
        <div class="map-placeholder">
            🚩 왼쪽에서 목적지를 입력하고 정보를 확인하세요.
        </div>
    """, unsafe_allow_html=True)
