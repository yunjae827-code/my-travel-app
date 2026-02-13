import streamlit as st
import requests
from geopy.geocoders import Nominatim

# --- [1] 페이지 및 테마 자동 대응 설정 ---
st.set_page_config(page_title="스마트 통합 가이드", layout="centered")

st.markdown("""
    <style>
    /* 다크/라이트 모드 공통 변수 설정 */
    :root {
        --card-bg: rgba(255, 255, 255, 0.1);
        --text-color: inherit;
        --accent-color: #2196f3;
    }
    
    /* 화면 중앙 집중형 레이아웃 */
    .main .block-container { max-width: 650px; padding-top: 3rem; }
    
    /* 테마에 반응하는 카드 디자인 */
    .content-card {
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background-color: var(--card-bg);
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* 날씨 카드 (반투명 스타일로 테마 무관 시인성 확보) */
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 15px; padding: 20px; 
        border-left: 8px solid var(--accent-color); 
        margin: 20px 0;
    }
    
    /* 상세 경로 단계 리스트 */
    .step-item {
        padding: 15px; border-bottom: 1px solid rgba(128, 128, 128, 0.1); 
        font-size: 0.95em; line-height: 1.6;
    }
    .step-num { color: #00c73c; font-weight: bold; margin-right: 10px; }
    
    /* 버튼 스타일 조정 */
    .stButton > button { width: 100%; border-radius: 8px; height: 3.2em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 데이터 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 실제 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url).json()
        return res if res.get("main") else None
    except: return None

def fetch_transit_steps(s_addr, d_addr):
    geolocator = Nominatim(user_agent="my_travel_v26")
    try:
        s_loc, d_loc = geolocator.geocode(s_addr), geolocator.geocode(d_addr)
        if s_loc and d_loc:
            url = f"http://router.project-osrm.org/route/v1/driving/{s_loc.longitude},{s_loc.latitude};{d_loc.longitude},{d_loc.latitude}?steps=true&languages=ko"
            res = requests.get(url).json()
            if res['code'] == 'Ok':
                return res['routes'][0]['legs'][0]['steps'], (d_loc.latitude, d_loc.longitude)
    except: pass
    return None, None

# --- [3] 메인 UI 레이아웃 (중앙 배치) ---
st.markdown("<h2 style='text-align: center;'>🚀 스마트 통합 가이드</h2>", unsafe_allow_html=True)

# 세션 상태 초기화 (기본값 설정)
if 'start' not in st.session_state: st.session_state.start = "출발지"
if 'dest' not in st.session_state: st.session_state.dest = "목적지"
if 'coords' not in st.session_state: st.session_state.coords = (37.5547, 126.9707)

with st.container():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    # 입력창
    st.session_state.start = st.text_input("📍 출발 지점", value=st.session_state.start)
    st.session_state.dest = st.text_input("🚩 도착 지점", value=st.session_state.dest)
    
    # 버튼 섹션 (가로 배치)
    col1, col2 = st.columns(2)
    with col1:
        search_btn = st.button("🔄 탐색 및 정보 갱신")
    with col2:
        # 목적지 이름 기반 구글 지도 보기 (새 창)
        map_url = f"https://www.google.co.kr/maps/search/{st.session_state.dest.replace(' ', '+')}/?hl=ko"
        st.link_button("🗺️ 지도보기", map_url)

    # 데이터 처리 및 결과 표시
    steps, coords = None, st.session_state.coords
    if search_btn:
        steps, new_coords = fetch_transit_steps(st.session_state.start, st.session_state.dest)
        if new_coords: st.session_state.coords = new_coords
        st.rerun()

    # 1. 날씨 정보 (버튼 바로 아래 배치)
    w = get_weather(st.session_state.coords[0], st.session_state.coords[1])
    if w:
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ {st.session_state.dest} 날씨</h4>
                <h2 style="margin:10px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']} | 습도 {w['main']['humidity']}%</p>
            </div>
        """, unsafe_allow_html=True)

    # 2. 상세 경로 가이드 (날씨 아래 고정)
    st.markdown("### 🚌 상세 이동 경로")
    # 검색 버튼을 누르지 않았더라도 기본 경로 리스트를 다시 가져옵니다.
    current_steps, _ = fetch_transit_steps(st.session_state.start, st.session_state.dest)
    
    if current_steps:
        for i, step in enumerate(current_steps):
            instr = step['maneuver']['instruction']
            dist = step['distance']
            st.markdown(f"""
                <div class="step-item">
                    <span class="step-num">{i+1}</span> {instr} <br>
                    <small style="opacity:0.7;">약 {dist:.0f}m 이동</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("상단 버튼을 눌러 상세 경로 리스트를 갱신하세요.")
            
    st.markdown('</div>', unsafe_allow_html=True)
