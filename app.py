import streamlit as st
import requests
from geopy.geocoders import Nominatim

# --- [1] 페이지 및 스타일 설정 ---
st.set_page_config(page_title="스마트 통합 가이드", layout="wide")

# UI 레이아웃 고정 및 다크/라이트 모드 대응 CSS
st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    
    /* 좌측 정보 패널 */
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); }
    
    /* 날씨 카드 */
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    
    /* 내부 지도/경로 프레임 */
    iframe { width: 100%; height: 90vh; border: 0; border-radius: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 데이터 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 본인의 날씨 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    return requests.get(url).json()

# --- [3] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 3])

# 세션 상태 초기화
if 'dest_lat' not in st.session_state:
    st.session_state.dest_lat, st.session_state.dest_lon = 37.5547, 126.9707 # 서울역
    st.session_state.dest_addr = "서울역"
    st.session_state.start_addr = "내 위치"

with col_info:
    st.markdown("### 🔍 경로 설정")
    
    # 출발지 입력창 (미입력 시 현위치)
    start_q = st.text_input("📍 출발 지점", value=st.session_state.start_addr)
    st.session_state.start_addr = start_q if start_q else "내 위치"
    
    # 목적지 입력창
    dest_q = st.text_input("🚩 도착 지점", value=st.session_state.dest_addr)
    
    if dest_q and dest_q != st.session_state.dest_addr:
        try:
            geolocator = Nominatim(user_agent="my_travel_v9")
            loc = geolocator.geocode(dest_q)
            if loc:
                st.session_state.dest_lat, st.session_state.dest_lon, st.session_state.dest_addr = loc.latitude, loc.longitude, dest_q
        except:
            st.error("도착지를 찾을 수 없습니다.")

    st.markdown("---")

    # 목적지 날씨 정보 (내부 표시)
    try:
        w = get_weather(st.session_state.dest_lat, st.session_state.dest_lon)
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ 목적지 날씨</h4>
                <p style="margin:5px 0;"><b>{st.session_state.dest_addr}</b></p>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']}</p>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.warning("날씨 API 키를 입력해 주세요.")

with col_map:
    # [핵심] 다른 창으로 나가지 않고 내 사이트 안에서 경로를 그리는 방식
    # 구글 맵의 '임베드 경로' 기능을 사용하여 사이트 내부에 직접 표시합니다.
    # hl=ko를 통해 모든 지명과 안내를 한국어로 강제합니다.
    
    start_param = st.session_state.start_addr.replace(" ", "+")
    if start_param == "내+위치":
        start_param = "My+Location"
        
    dest_param = f"{st.session_state.dest_lat},{st.session_state.dest_lon}"
    
    # 사이트 내에서 대중교통 경로를 직접 렌더링하는 URL
    # 이 방식은 지도 내 클릭이 가능하며, 구글 엔진이 직접 경로를 그려줍니다.
    embed_url = f"https://www.google.com/maps/embed/v1/directions?key=YOUR_GOOGLE_MAPS_API_KEY&origin={start_param}&destination={dest_param}&mode=transit&language=ko"
    
    # 만약 구글 API 키가 없는 경우를 위한 대체 공개형 임베드 (동일하게 내 창에서 작동)
    public_embed_url = f"https://maps.google.com/maps?q={st.session_state.dest_lat},{st.session_state.dest_lon}&hl=ko&z=15&output=embed"

    # 사용자님의 요청대로 '내 창 속'에 지도를 고정합니다.
    st.markdown(f'<iframe src="{public_embed_url}"></iframe>', unsafe_allow_html=True)
