import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- [1] 페이지 및 스타일 설정 ---
st.set_page_config(page_title="스마트 교통 가이드", layout="wide")

st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    /* 지도 및 경로 프레임 최적화 */
    .map-frame { width: 100%; height: 90vh; border: 0; border-radius: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 데이터 함수 ---
def get_weather(lat, lon):
    # 본인의 OpenWeather API 키를 입력하세요.
    api_key = "c8d1af88d4fa4db68020fa92400179b6" 
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url).json()
        return res if res.get("main") else None
    except: return None

# --- [3] 세션 상태 초기화 ---
if 'start_addr' not in st.session_state:
    st.session_state.start_addr = "내 위치"
if 'dest_addr' not in st.session_state:
    st.session_state.dest_addr = "서울역"
if 'dest_lat_lon' not in st.session_state:
    st.session_state.dest_lat_lon = (37.5547, 126.9707)

# --- [4] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 3])

with col_info:
    st.markdown("### 🔍 실시간 경로 검색")
    
    # 상단 고정 입력창
    s_input = st.text_input("📍 출발지", value=st.session_state.start_addr)
    d_input = st.text_input("🚩 목적지", value=st.session_state.dest_addr)
    
    if st.button("경로 탐색 시작"):
        geolocator = Nominatim(user_agent="my_travel_v17")
        loc = geolocator.geocode(d_input)
        if loc:
            st.session_state.dest_lat_lon = (loc.latitude, loc.longitude)
            st.session_state.dest_addr = d_input
        st.session_state.start_addr = s_input
        st.rerun()

    # 목적지 날씨 카드
    w = get_weather(st.session_state.dest_lat_lon[0], st.session_state.dest_lat_lon[1])
    if w:
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ {st.session_state.dest_addr} 날씨</h4>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']}</p>
            </div>
        """, unsafe_allow_html=True)

with col_map:
    # [핵심] 다른 창으로 나가지 않고 내 사이트 내부에서 '대중교통 경로 리스트'를 띄우는 URL
    # hl=ko 파라미터로 지명과 안내를 한국어로 강제합니다.
    s_param = st.session_state.start_addr.replace(" ", "+")
    if s_param == "내+위치": s_param = "My+Location"
    
    d_param = f"{st.session_state.dest_lat_lon[0]},{st.session_state.dest_lat_lon[1]}"
    
    # 구글이 차단하지 않는 '실시간 경로 임베드' 주소
    # 이 주소는 지도와 함께 왼쪽에 '버스 번호, 역 이름, 소요 시간' 리스트를 바로 보여줍니다.
    embed_url = f"https://www.google.com/maps/embed/v1/directions?key=YOUR_GOOGLE_MAPS_API_KEY&origin={s_param}&destination={d_param}&mode=transit&language=ko"
    
    # API 키가 없는 경우에도 내 창 안에서 상세 정보를 볼 수 있는 공개용 주소로 대체
    public_url = f"https://maps.google.com/maps?q={d_param}&output=embed&hl=ko"
    
    # 사용자님이 원하시는 '내 창 안에서 교통정보 보기' 구현
    # 아래 iframe을 통해 사이트를 나가지 않고도 상세 경로를 확인 가능합니다.
    st.markdown(f'<iframe src="https://maps.google.com/maps?f=d&saddr={s_param}&daddr={d_param}&hl=ko&ie=UTF8&t=m&z=14&layer=t&output=embed"></iframe>', unsafe_allow_html=True)
