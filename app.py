import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- [1] 페이지 설정 및 스타일 ---
st.set_page_config(page_title="스마트 올인원 가이드", layout="wide")

st.markdown("""
    <style>
    :root { --text-color: inherit; }
    .main .block-container { padding: 0; height: 100vh; overflow: hidden; color: var(--text-color); }
    .info-panel { padding: 20px; height: 100vh; background-color: rgba(128,128,128,0.05); border-right: 1px solid rgba(128,128,128,0.2); overflow-y: auto; }
    .weather-card { 
        background-color: rgba(33, 150, 243, 0.15); 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 6px solid #2196f3; 
    }
    /* 상세 경로 가이드 프레임 */
    .guide-frame { width: 100%; height: 85vh; border: 0; border-radius: 10px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 세션 및 데이터 함수 ---
if 'start_loc' not in st.session_state:
    st.session_state.start_loc = {"lat": 37.5665, "lon": 126.9780, "addr": "서울시청"}
if 'dest_loc' not in st.session_state:
    st.session_state.dest_loc = {"lat": 37.5547, "lon": 126.9707, "addr": "서울역"}
if 'last_clicked' not in st.session_state:
    st.session_state.last_clicked = None

def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 실제 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try: return requests.get(url).json()
    except: return None

# --- [3] 메인 레이아웃 ---
col_info, col_map = st.columns([1.2, 2.8])

with col_info:
    st.markdown("### 🔍 통합 경로 설정")
    s_in = st.text_input("📍 출발 지점", value=st.session_state.start_loc['addr'])
    d_in = st.text_input("🚩 도착 지점", value=st.session_state.dest_loc['addr'])
    
    if st.button("탐색 실행 및 날씨 갱신"):
        geolocator = Nominatim(user_agent="my_final_guide_2026")
        ls, ld = geolocator.geocode(s_in), geolocator.geocode(d_in)
        if ls: st.session_state.start_loc = {"lat": ls.latitude, "lon": ls.longitude, "addr": s_in}
        if ld: st.session_state.dest_loc = {"lat": ld.latitude, "lon": ld.longitude, "addr": d_in}
        st.rerun()

    # 날씨 정보
    w = get_weather(st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon'])
    if w and 'main' in w:
        st.markdown(f"""<div class="weather-card">
            <h4>🌤️ {st.session_state.dest_loc['addr']} 날씨</h4>
            <h2 style="margin:5px 0;">{w['main']['temp']}°C</h2>
            <p>{w['weather'][0]['description']}</p>
        </div>""", unsafe_allow_html=True)

    # 클릭 시 출발/도착 지정 버튼
    if st.session_state.last_clicked:
        lat, lon = st.session_state.last_clicked
        st.write(f"📍 선택됨: {lat:.4f}, {lon:.4f}")
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
    # 탭을 사용하여 지도와 상세 리스트를 한 화면에서 제공
    tab_map, tab_route = st.tabs(["🗺️ 한글 지도", "🚇 상세 경로 리스트"])
    
    with tab_map:
        m = folium.Map(
            location=[st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], 
            zoom_start=14,
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=ko", 
            attr="Google Maps"
        )
        folium.Marker([st.session_state.start_loc['lat'], st.session_state.start_loc['lon']], icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], icon=folium.Icon(color='red')).add_to(m)
        
        map_data = st_folium(m, width="100%", height=750, returned_objects=["last_clicked"])
        if map_data and map_data.get("last_clicked"):
            st.session_state.last_clicked = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
            st.rerun()

    with tab_route:
        # [핵심] 연결 거부 없이 상세 경로(버스/지하철/시간)를 '내 창'에 띄우는 모바일 뷰 주소
        s_addr = st.session_state.start_loc['addr'].replace(" ", "+")
        d_addr = st.session_state.dest_loc['addr'].replace(" ", "+")
        
        # 이 주소는 구글이 iframe 차단을 덜 하는 검색 결과 기반 경로 주소입니다.
        route_url = f"https://www.google.co.kr/maps/dir/{s_addr}/{d_addr}/@37.5,127,12z/data=!4m2!4m1!3e3?hl=ko"
        
        # 실제 사이트 내부 임베드 (가장 안정적인 형식)
        st.markdown(f'<iframe class="guide-frame" src="https://maps.google.com/maps?q={d_addr}&output=embed&hl=ko"></iframe>', unsafe_allow_html=True)
        st.info(f"💡 {st.session_state.start_loc['addr']} → {st.session_state.dest_loc['addr']} 실시간 상세 경로는 아래 버튼을 통해 현재 페이지에서 확인하세요.")
        st.link_button("🚌 실시간 버스/지하철 상세 정보 열기", route_url)
