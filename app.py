import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- [1] 페이지 설정 ---
st.set_page_config(page_title="스마트 경로 가이드", layout="wide")

# UI 스타일 설정 (다크모드 대응 및 지도 최적화)
st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 10px; border-left: 6px solid #2196f3; 
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 세션 상태 초기화 ---
if 'start_loc' not in st.session_state:
    st.session_state.start_loc = {"lat": 37.5665, "lon": 126.9780, "addr": "서울시청 (기본값)"}
if 'dest_loc' not in st.session_state:
    st.session_state.dest_loc = {"lat": 37.5547, "lon": 126.9707, "addr": "서울역 (기본값)"}
if 'map_mode' not in st.session_state:
    st.session_state.map_mode = "목적지 선택"

# --- [3] 데이터 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 실제 키 입력 필요
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try: return requests.get(url).json()
    except: return None

# --- [4] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 2.5])

with col_info:
    st.markdown("### 🗺️ 스마트 경로 설정")
    
    # [기능 1] 현위치 GPS 버튼 (브라우저 기능 활용 안내)
    if st.button("📍 내 주변으로 지도 이동"):
        st.info("브라우저의 GPS를 활성화하면 현재 위치 주변을 탐색할 수 있습니다.")

    st.markdown("---")
    
    # [기능 2] 출발지/목적지 선택 모드 전환
    st.session_state.map_mode = st.radio("지도에서 클릭 시 설정할 항목:", ["출발지 선택", "목적지 선택"])
    
    st.success(f"🚩 **출발:** {st.session_state.start_loc['addr']}")
    st.error(f"🏁 **도착:** {st.session_state.dest_loc['addr']}")

    # 날씨 정보
    w = get_weather(st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon'])
    if w and 'main' in w:
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ 목적지 실시간 날씨</h4>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p style="margin:0;">{w['weather'][0]['description']}</p>
            </div>
        """, unsafe_allow_html=True)

    # [기능 3] 경로 보기 버튼
    route_url = f"https://www.google.com/maps/dir/{st.session_state.start_loc['lat']},{st.session_state.start_loc['lon']}/{st.session_state.dest_loc['lat']},{st.session_state.dest_loc['lon']}/"
    st.markdown(f'<a href="{route_url}" target="_blank"><button style="width:100%; padding:12px; background:#2196f3; color:white; border:none; border-radius:8px; cursor:pointer;">🚇 실시간 상세 경로 확인</button></a>', unsafe_allow_html=True)

with col_map:
    # 휠 스크롤이 즉시 허용되는 Folium 지도
    m = folium.Map(location=[st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], zoom_start=14)
    
    # 출발지 마커 (파란색)
    folium.Marker([st.session_state.start_loc['lat'], st.session_state.start_loc['lon']], 
                  popup="출발지", icon=folium.Icon(color='blue', icon='play')).add_to(m)
    
    # 목적지 마커 (빨간색)
    folium.Marker([st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], 
                  popup="목적지", icon=folium.Icon(color='red', icon='stop')).add_to(m)

    # 지도를 클릭하면 좌표를 가져오는 기능
    m.add_child(folium.LatLngPopup())
    
    # 지도 렌더링 (휠 스크롤 즉시 허용)
    map_data = st_folium(m, width="100%", height=800, returned_objects=["last_clicked"])

    # [기능 4] 지도 클릭 시 현위치/목적지 자동 입력
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        
        if st.session_state.map_mode == "출발지 선택":
            st.session_state.start_loc = {"lat": lat, "lon": lon, "addr": f"{lat:.4f}, {lon:.4f} (지도 선택 지점)"}
        else:
            st.session_state.dest_loc = {"lat": lat, "lon": lon, "addr": f"{lat:.4f}, {lon:.4f} (지도 선택 지점)"}
        st.rerun()
