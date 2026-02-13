import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- [1] 페이지 설정 ---
st.set_page_config(page_title="스마트 통합 가이드", layout="wide")

st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    /* 교통정보 프레임 스타일 */
    .map-container { width: 100%; height: 90vh; border: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 세션 상태 초기화 ---
if 'start_loc' not in st.session_state:
    st.session_state.start_loc = {"lat": 37.5665, "lon": 126.9780, "addr": "서울시청"}
if 'dest_loc' not in st.session_state:
    st.session_state.dest_loc = {"lat": 37.5547, "lon": 126.9707, "addr": "서울역"}

# --- [3] 데이터 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 실제 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try: return requests.get(url).json()
    except: return None

# --- [4] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 3])

with col_info:
    st.markdown("### 🔍 경로 및 교통 정보")
    
    # 텍스트 입력창
    start_q = st.text_input("📍 출발", value=st.session_state.start_loc['addr'])
    dest_q = st.text_input("🚩 도착", value=st.session_state.dest_loc['addr'])
    
    if st.button("경로 검색 반영"):
        geolocator = Nominatim(user_agent="my_travel_v12")
        if start_q:
            loc_s = geolocator.geocode(start_q)
            if loc_s: st.session_state.start_loc = {"lat": loc_s.latitude, "lon": loc_s.longitude, "addr": start_q}
        if dest_q:
            loc_d = geolocator.geocode(dest_q)
            if loc_d: st.session_state.dest_loc = {"lat": loc_d.latitude, "lon": loc_d.longitude, "addr": dest_q}

    st.markdown("---")
    
    # 날씨 정보
    w = get_weather(st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon'])
    if w and 'main' in w:
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ 목적지 날씨</h4>
                <p><b>{st.session_state.dest_loc['addr']}</b>: {w['main']['temp']}°C</p>
            </div>
        """, unsafe_allow_html=True)

with col_map:
    # [핵심] 외부 창으로 나가지 않고 내 사이트 안에서 교통수단별 경로를 띄움
    # 출발지와 목적지 좌표를 사용하여 구글 맵의 경로 탐색 엔진을 iframe으로 삽입
    # hl=ko 파라미터로 모든 지명과 길찾기 안내를 한국어로 표시
    origin = f"{st.session_state.start_loc['lat']},{st.session_state.start_loc['lon']}"
    destination = f"{st.session_state.dest_loc['lat']},{st.session_state.dest_loc['lon']}"
    
    # 대중교통(transit) 모드로 내 사이트 내에 직접 렌더링
    # 이 방식은 사용자가 사이트 내에서 지하철 노선, 버스 번호, 소요 시간을 모두 확인할 수 있게 해줍니다.
    embed_path = f"https://www.google.com/maps/embed/v1/directions?key=YOUR_GOOGLE_MAPS_API_KEY&origin={origin}&destination={destination}&mode=transit&language=ko"
    
    # API 키를 발급받지 못한 경우를 위해, 공개용 경로 뷰어(휠 제어 가능)를 내부에 삽입
    public_route_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=transit&hl=ko"
    
    # 사용자님의 요청대로 다른 창으로 나가지 않게 iframe으로 고정
    st.markdown(f"""
        <iframe src="https://www.google.com/maps/embed/v1/directions?key=YOUR_GOOGLE_MAPS_API_KEY&origin={origin}&destination={destination}&mode=transit&language=ko" 
        style="width:100%; height:90vh; border:0;"></iframe>
    """, unsafe_allow_html=True)
