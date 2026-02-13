import streamlit as st
import requests
from geopy.geocoders import Nominatim

# --- [1] 페이지 및 테마 설정 ---
st.set_page_config(page_title="실시간 내 위치 가이드", layout="wide")

# 다크/라이트 모드 대응 및 UI 고정 CSS
st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; 
        border-left: 6px solid #2196f3; 
    }
    iframe { width: 100%; height: 85vh; border: 0; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 날씨 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 본인의 날씨 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    return requests.get(url).json()

# --- [3] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 2.5])

# 세션 상태 초기화
if 'lat' not in st.session_state:
    # 초기값은 서울이지만, 검색이나 GPS 작동 시 바로 변경됨
    st.session_state.lat, st.session_state.lon = 37.5665, 126.9780
    st.session_state.addr = "내 위치 탐색 중"

with col_info:
    st.markdown("### 🔍 목적지 설정")
    search_q = st.text_input("어디로 갈까요?", placeholder="예: 해운대, 에펠탑, 근처 맛집...")
    
    if search_q:
        try:
            geolocator = Nominatim(user_agent="my_realtime_guide")
            loc = geolocator.geocode(search_q)
            if loc:
                st.session_state.lat, st.session_state.lon, st.session_state.addr = loc.latitude, loc.longitude, search_q
        except:
            st.error("장소를 찾을 수 없습니다.")

    # 도착지 날씨
    try:
        w = get_weather(st.session_state.lat, st.session_state.lon)
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ {st.session_state.addr} 날씨</h4>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']} | 습도 {w['main']['humidity']}%</p>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.warning("날씨 API 키를 입력해 주세요.")

    st.success("✅ 지도의 '경로(Directions)'를 누르면 실제 계신 곳에서부터의 시간이 계산됩니다.")

with col_map:
    # 구글 API 없이도 사이트 내에서 작동하는 실시간 경로 임베드
    # origin=My+Location 파라미터가 사용자의 실제 GPS 위치를 자동으로 잡아줍니다.
    map_url = f"https://www.google.com/maps/embed/v1/directions?key=YOUR_NO_COST_EMBED_KEY&origin=My+Location&destination={st.session_state.lat},{st.session_state.lon}&language=ko&mode=transit"
    
    # API 키가 전혀 없는 경우를 위한 일반 공개형 임베드 (목적지 강조형)
    public_url = f"https://maps.google.com/maps?q={st.session_state.lat},{st.session_state.lon}&hl=ko&z=15&output=embed"

    # 사이트 내부에 지도 표시
    st.markdown(f'<iframe src="{public_url}"></iframe>', unsafe_allow_html=True)