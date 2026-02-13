import streamlit as st
import requests
from geopy.geocoders import Nominatim

# --- [1] 페이지 및 스타일 설정 ---
st.set_page_config(page_title="스마트 여행 가이드", layout="wide")

st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    .facility-btn {
        width: 100%; border: 1px solid #ddd; border-radius: 8px; padding: 10px;
        margin-bottom: 8px; background-color: white; cursor: pointer; color: black;
        font-weight: bold; text-align: center; display: block; text-decoration: none;
    }
    .facility-btn:hover { background-color: #f0f0f0; }
    iframe { width: 100%; height: 85vh; border: 0; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 데이터 처리 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 본인의 날씨 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    return requests.get(url).json()

# --- [3] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 2.5])

# 세션 상태 초기화 (기본값: 서울역)
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 37.5547, 126.9707
    st.session_state.addr = "서울역"
if 'search_type' not in st.session_state:
    st.session_state.search_type = "place" # 일반 장소 검색 모드

with col_info:
    st.markdown("### 🔍 어디로 갈까요?")
    search_q = st.text_input("목적지 입력", placeholder="예: 해운대, 에펠탑...")
    
    if search_q:
        try:
            geolocator = Nominatim(user_agent="my_travel_v6")
            loc = geolocator.geocode(search_q)
            if loc:
                st.session_state.lat, st.session_state.lon, st.session_state.addr = loc.latitude, loc.longitude, search_q
                st.session_state.search_type = "place"
        except:
            st.error("장소를 찾을 수 없습니다.")

    # 날씨 카드
    try:
        w = get_weather(st.session_state.lat, st.session_state.lon)
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ {st.session_state.addr} 날씨</h4>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']}</p>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.warning("날씨 API 키를 설정해주세요.")

    # 주변 시설 검색 버튼 (내 사이트 내부 지도 연동)
    st.markdown("### 📍 주변 시설 찾기")
    if st.button("🏪 주변 편의점 보기"):
        st.session_state.search_type = "convenience_store"
    if st.button("🚻 주변 공중화장실 보기"):
        st.session_state.search_type = "toilet"
    if st.button("☕ 주변 카페 보기"):
        st.session_state.search_type = "cafe"

with col_map:
    # 검색 타입에 따른 지도 URL 생성 (공개형 임베드 방식)
    if st.session_state.search_type == "place":
        # 일반 목적지 강조 모드
        map_url = f"https://maps.google.com/maps?q={st.session_state.lat},{st.session_state.lon}&hl=ko&z=15&output=embed"
    else:
        # 특정 시설 검색 모드 (현위치 혹은 목적지 기준)
        facility_query = {
            "convenience_store": "편의점",
            "toilet": "공중화장실",
            "cafe": "카페"
        }.get(st.session_state.search_type, "")
        
        # 지도를 사이트 내에서 검색 결과 모드로 전환
        map_url = f"https://maps.google.com/maps?q={facility_query}+near+{st.session_state.lat},{st.session_state.lon}&hl=ko&z=15&output=embed"

    # 사이트 내부에 실시간 지도 렌더링
    st.markdown(f'<iframe src="{map_url}"></iframe>', unsafe_allow_html=True)