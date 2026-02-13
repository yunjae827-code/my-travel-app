import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- [1] 페이지 설정 및 스타일 ---
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
    /* 팝업 버튼 스타일 */
    .popup-btn { 
        padding: 5px 10px; margin: 2px; border: none; border-radius: 4px; 
        color: white; cursor: pointer; font-size: 12px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 세션 상태 초기화 ---
if 'start_loc' not in st.session_state:
    st.session_state.start_loc = {"lat": 37.5665, "lon": 126.9780, "addr": "서울시청 (기본)"}
if 'dest_loc' not in st.session_state:
    st.session_state.dest_loc = {"lat": 37.5547, "lon": 126.9707, "addr": "서울역 (기본)"}
if 'clicked_lat' not in st.session_state:
    st.session_state.clicked_lat, st.session_state.clicked_lon = None, None

# --- [3] 날씨 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 본인의 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try: return requests.get(url).json()
    except: return None

# --- [4] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 3])

with col_info:
    st.markdown("### 🔍 경로 설정")
    
    # [입력창] 텍스트 입력으로 위치 변경 가능
    start_q = st.text_input("📍 출발 지점", value=st.session_state.start_loc['addr'])
    dest_q = st.text_input("🚩 도착 지점", value=st.session_state.dest_loc['addr'])
    
    # 검색 로직 (입력값이 바뀌었을 때만 작동)
    geolocator = Nominatim(user_agent="my_travel_v10")
    if start_q != st.session_state.start_loc['addr']:
        loc = geolocator.geocode(start_q)
        if loc: st.session_state.start_loc = {"lat": loc.latitude, "lon": loc.longitude, "addr": start_q}
    if dest_q != st.session_state.dest_loc['addr']:
        loc = geolocator.geocode(dest_q)
        if loc: st.session_state.dest_loc = {"lat": loc.latitude, "lon": loc.longitude, "addr": dest_q}

    st.markdown("---")
    
    # 목적지 날씨 정보
    w = get_weather(st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon'])
    if w and 'main' in w:
        st.markdown(f"""
            <div class="weather-card">
                <h4 style="margin:0;">🌤️ 목적지 날씨</h4>
                <p><b>{st.session_state.dest_loc['addr']}</b></p>
                <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
                <p>{w['weather'][0]['description']}</p>
            </div>
        """, unsafe_allow_html=True)

    # 사이트 내부 경로 표시를 위한 정보 제공
    st.info("💡 지도에서 건물을 클릭하면 나타나는 팝업에서 '출발' 또는 '도착'을 지정하세요.")

with col_map:
    # 한글 지명이 지원되는 Folium 지도 생성
    m = folium.Map(
        location=[st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], 
        zoom_start=14,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=ko", # 구글 한글 지도 타일 적용
        attr="Google Maps"
    )
    
    # 출발/도착지 마커 표시
    folium.Marker([st.session_state.start_loc['lat'], st.session_state.start_loc['lon']], 
                  popup="출발지", icon=folium.Icon(color='blue', icon='play')).add_to(m)
    folium.Marker([st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], 
                  popup="목적지", icon=folium.Icon(color='red', icon='stop')).add_to(m)

    # 지도 클릭 이벤트 처리 (좌표 추출 전용)
    m.add_child(folium.LatLngPopup())
    
    # 지도 렌더링
    map_data = st_folium(m, width="100%", height=850, returned_objects=["last_clicked"])

    # [핵심] 지도 클릭 시 팝업과 버튼 인터랙션
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        
        # 지도 우측 상단이나 정보창 근처에 '선택된 좌표'용 버튼 생성
        st.write(f"📍 선택된 지점: {lat:.4f}, {lon:.4f}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔵 이곳을 출발지로"):
                st.session_state.start_loc = {"lat": lat, "lon": lon, "addr": f"지도 선택 ({lat:.3f})"}
                st.rerun()
        with c2:
            if st.button("🔴 이곳을 도착지로"):
                st.session_state.dest_loc = {"lat": lat, "lon": lon
    st.markdown(f'<iframe src="{public_embed_url}"></iframe>', unsafe_allow_html=True)

