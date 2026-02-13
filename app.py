import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- [1] 페이지 설정 및 스타일 ---
st.set_page_config(page_title="스마트 통합 교통 가이드", layout="wide")

st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); overflow-y: auto; }
    
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; margin-top: 5px; }
    iframe { width: 100%; height: 85vh; border: 0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 세션 상태 초기화 ---
if 'start_loc' not in st.session_state:
    st.session_state.start_loc = {"lat": 37.5665, "lon": 126.9780, "addr": "서울시청"}
if 'dest_loc' not in st.session_state:
    st.session_state.dest_loc = {"lat": 37.5547, "lon": 126.9707, "addr": "서울역"}
if 'last_clicked' not in st.session_state:
    st.session_state.last_clicked = None

# --- [3] 데이터 함수 ---
def get_weather(lat, lon):
    # 실제 OpenWeatherMap API 키를 입력하세요.
    api_key = "c8d1af88d4fa4db68020fa92400179b6" 
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url).json()
        if res.get("main"):
            return res
    except:
        return None
    return None

# --- [4] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 2.8])

with col_info:
    st.markdown("### 🔍 경로 및 날씨")
    
    # 출발지/목적지 직접 입력 칸
    start_q = st.text_input("📍 출발 지점", value=st.session_state.start_loc['addr'])
    dest_q = st.text_input("🚩 도착 지점", value=st.session_state.dest_loc['addr'])
    
    if st.button("검색 결과로 경로 찾기"):
        geolocator = Nominatim(user_agent="my_travel_v15")
        loc_s = geolocator.geocode(start_q)
        loc_d = geolocator.geocode(dest_q)
        if loc_s: st.session_state.start_loc = {"lat": loc_s.latitude, "lon": loc_s.longitude, "addr": start_q}
        if loc_d: st.session_state.dest_loc = {"lat": loc_d.latitude, "lon": loc_d.longitude, "addr": dest_q}
        st.rerun()

    # 목적지 날씨 카드 표시
    w = get_weather(st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon'])
    if w:
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ {st.session_state.dest_loc['addr']} 날씨</h4>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']} | 습도 {w['main']['humidity']}%</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("날씨 API 키를 입력하면 기온이 표시됩니다.")

    # 지도 클릭 시 좌표 및 버튼 생성
    if st.session_state.last_clicked:
        lat, lon = st.session_state.last_clicked
        st.markdown(f"**📍 선택된 지점**: `{lat:.4f}, {lon:.4f}`")
        c1, c2 = st.columns(2)
        if c1.button("출발지로"):
            st.session_state.start_loc = {"lat": lat, "lon": lon, "addr": "지도 선택 지점"}
            st.session_state.last_clicked = None
            st.rerun()
        if c2.button("도착지로"):
            st.session_state.dest_loc = {"lat": lat, "lon": lon, "addr": "지도 선택 지점"}
            st.session_state.last_clicked = None
            st.rerun()

with col_map:
    # 탭 메뉴를 통해 '지도 보기'와 '상세 경로 리스트'를 한 창에서 전환
    tab1, tab2 = st.tabs(["🗺️ 한글 지도", "🚌 상세 경로 가이드"])
    
    with tab1:
        # 한글 지명이 지원되는 인터랙티브 지도 (휠 스크롤 즉시 허용)
        m = folium.Map(
            location=[st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], 
            zoom_start=14,
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=ko", 
            attr="Google Maps"
        )
        folium.Marker([st.session_state.start_loc['lat'], st.session_state.start_loc['lon']], popup="출발", icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], popup="도착", icon=folium.Icon(color='red')).add_to(m)
        
        # 지도 렌더링
        map_data = st_folium(m, width="100%", height=750, returned_objects=["last_clicked"])
        if map_data and map_data.get("last_clicked"):
            click = map_data["last_clicked"]
            st.session_state.last_clicked = (click["lat"], click["lng"])
            st.rerun()

    with tab2:
        # 내 사이트 안에서 상세 경로(버스 번호, 지하철 역, 방면, 시간)를 보여주는 프레임
        origin = f"{st.session_state.start_loc['lat']},{st.session_state.start_loc['lon']}"
        dest = f"{st.session_state.dest_loc['lat']},{st.session_state.dest_loc['lon']}"
        
        # 상세 경로 리스트 임베드 (hl=ko로 한글 가이드 고정)
        # 이 창에서 어떤 버스를 타야 하는지, 어느 역에서 내리는지 모두 나옵니다.
        embed_url = f"https://www.google.com/maps/embed/v1/directions?key=YOUR_GOOGLE_MAPS_API_KEY&origin={origin}&destination={dest}&mode=transit&language=ko"
        
        # API 키가 없는 경우에도 내 사이트 안에서 상세 경로 리스트를 볼 수 있는 주소
        public_route_url = f"https://www.google.com/maps/dir/?api=1&destination=3{origin}&daddr={dest}&hl=ko&ie=UTF8&t=m&z=14&layer=t&output=embed"
        
        st.markdown(f'<iframe src="{public_route_url}"></iframe>', unsafe_allow_html=True)
