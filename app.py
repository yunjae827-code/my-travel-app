import streamlit as st
import requests
from geopy.geocoders import Nominatim

# --- [1] 페이지 설정 ---
st.set_page_config(page_title="스마트 통합 가이드", layout="centered") # 화면 중앙 배치

st.markdown("""
    <style>
    /* 전체 배경 및 중앙 정렬 보정 */
    .stApp { background-color: #f9f9f9; }
    .main .block-container { padding-top: 5rem; max-width: 600px; }
    
    /* 카드형 디자인 */
    .content-card {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* 날씨 카드 */
    .weather-card { 
        background-color: #e3f2fd; 
        border-radius: 12px; padding: 20px; border-left: 6px solid #2196f3;
        margin-top: 20px;
    }
    
    /* 버튼 가로 정렬 */
    .stButton > button { width: 100%; border-radius: 8px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 데이터 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 실제 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url).json()
        if res.get("main"): return res
    except: return None
    return None

# --- [3] 세션 상태 ---
if 'start_addr' not in st.session_state: st.session_state.start_addr = "출발지"
if 'dest_addr' not in st.session_state: st.session_state.dest_addr = "목적지"
if 'coords' not in st.session_state: st.session_state.coords = (37.5547, 126.9707)

# --- [4] 화면 중앙 콘텐츠 ---
st.markdown("<h2 style='text-align: center;'>🗺️ 스마트 통합 가이드</h2>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    # 입력 필드
    s_input = st.text_input("📍 출발 지점", value=st.session_state.start_addr)
    d_input = st.text_input("🚩 도착 지점", value=st.session_state.dest_addr)
    
    # 버튼 섹션 (가로 배치)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 탐색 및 정보 갱신"):
            geolocator = Nominatim(user_agent="my_travel_v23")
            loc = geolocator.geocode(d_input)
            if loc:
                st.session_state.coords = (loc.latitude, loc.longitude)
                st.session_state.dest_addr = d_input
            st.session_state.start_addr = s_input
            st.rerun()
            
    with col2:
        # 구글 지도 보기 버튼 (새 창 열기)
        map_view_url = f"https://www.google.com/maps/search/{st.session_state.dest_addr.replace(' ', '+')}"
        st.link_button("🗺️ 지도보기", map_view_url)

    # 날씨 및 상세 정보 섹션
    w = get_weather(st.session_state.coords[0], st.session_state.coords[1])
    if w:
        st.markdown(
