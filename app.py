import streamlit as st
import requests
from geopy.geocoders import Nominatim

# --- [1] 페이지 및 테마 설정 ---
st.set_page_config(page_title="스마트 경로 가이드", layout="wide")

# 다크/라이트 모드 자동 대응 및 UI 고정 (화면 높이에 맞춘 지도 설정)
st.markdown("""
    <style>
    /* 시스템 테마에 따라 텍스트 색상 자동 조절 */
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); }
    
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; 
        border-left: 6px solid #2196f3; 
    }
    
    /* 지도 영역 높이 및 휠 스크롤 활성화 */
    iframe { width: 100%; height: 90vh; border: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 날씨 데이터 함수 ---
def get_weather(lat, lon):
    # 발급받으신 OpenWeather API 키를 입력하세요
    api_key = "c8d1af88d4fa4db68020fa92400179b6" 
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    return requests.get(url).json()

# --- [3] 메인 화면 레이아웃 ---
col_info, col_map = st.columns([1, 2.5])

# 세션 상태 초기화 (기본값: 서울역)
if 'dest_lat' not in st.session_state:
    st.session_state.dest_lat, st.session_state.dest_lon = 37.5547, 126.9707
    st.session_state.dest_addr = "서울역"
    st.session_state.start_addr = "My+Location"

with col_info:
    st.markdown("### 🗺️ 경로 및 날씨 설정")
    
    # 📍 출발지 설정
    # 사용자가 입력하지 않으면 'My Location'(현위치)이 출발지가 됩니다.
    start_input = st.text_input("📍 출발지 (출발 지점)", placeholder="미입력 시 '현위치' 기준")
    if start_input:
        st.session_state.start_addr = start_input.replace(" ", "+")
    else:
        st.session_state.start_addr = "My+Location"

    # 🚩 목적지 설정
    dest_input = st.text_input("🚩 목적지 (도착 지점)", placeholder="예: 해운대, 에펠탑, 강남역")
    if dest_input:
        try:
            geolocator = Nominatim(user_agent="my_travel_app_2026")
            loc = geolocator.geocode(dest_input)
            if loc:
                st.session_state.dest_lat, st.session_state.dest_lon, st.session_state.dest_addr = loc.latitude, loc.longitude, dest_input
        except:
            st.error("장소를 찾을 수 없습니다.")

    st.markdown("---")

    # 목적지 날씨 카드 출력
    try:
        w = get_weather(st.session_state.dest_lat, st.session_state.dest_lon)
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ 목적지 날씨</h4>
                <p style="margin:5px 0; font-weight:bold;">{st.session_state.dest_addr}</p>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']} | 습도 {w['main']['humidity']}%</p>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.warning("날씨 API 키를 입력해 주세요.")

with col_map:
    # 한국어 지명 및 휠 확대/축소가 지원되는 공개형 지도 임베드
    map_url = f"https://maps.google.com/maps?q={st.session_state.dest_lat},{st.session_state.dest_lon}&hl=ko&z=15&output=embed"

    st.markdown(f'<iframe src="{map_url}"></iframe>', unsafe_allow_html=True)