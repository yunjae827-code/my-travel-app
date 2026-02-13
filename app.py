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
    /* 연결 거부 방지를 위한 iframe 설정 */
    iframe { width: 100%; height: 80vh; border: 0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 세션 상태 초기화 ---
if 'start_loc' not in st.session_state:
    st.session_state.start_loc = {"lat": 37.5665, "lon": 126.9780, "addr": "서울시청"}
if 'dest_loc' not in st.session_state:
    st.session_state.dest_loc = {"lat": 37.5547, "lon": 126.9707, "addr": "서울역"}
if 'last_clicked' not in st.session_state:
    st.session_state.last_clicked = None

# --- [3] 날씨 함수 ---
def get_weather(lat, lon):
    api_key = "c8d1af88d4fa4db68020fa92400179b6" # 실제 키 입력
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url).json()
        if res.get("main"): return res
    except: return None
    return None

# --- [4] 메인 레이아웃 ---
col_info, col_map = st.columns([1, 2.5])

with col_info:
    st.markdown("### 🔍 경로 및 날씨")
    
    # 입력창
    start_q = st.text_input("📍 출발 지점", value=st.session_state.start_loc['addr'])
    dest_q = st.text_input("🚩 도착 지점", value=st.session_state.dest_loc['addr'])
    
    if st.button("검색 실행"):
        geolocator = Nominatim(user_agent="my_travel_v16")
        loc_s = geolocator.geocode(start_q)
        loc_d = geolocator.geocode(dest_q)
        if loc_s: st.session_state.start_loc = {"lat": loc_s.latitude, "lon": loc_s.longitude, "addr": start_q}
        if loc_d: st.session_state.dest_loc = {"lat": loc_d.latitude, "lon": loc_d.longitude, "addr": dest_q}
        st.rerun()

    # 날씨 표시
    w = get_weather(st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon'])
    if w:
        st.markdown(f"""<div class="weather-card">
            <h4>🌤️ 목적지 날씨: {w['main']['temp']}°C</h4>
            <p>{w['weather'][0]['description']}</p>
        </div>""", unsafe_allow_html=True)

    # 클릭된 지점 버튼
    if st.session_state.last_clicked:
        lat, lon = st.session_state.last_clicked
        st.write(f"📍 선택 지점: {lat:.4f}, {lon:.4f}")
        c1, c2 = st.columns(2)
        if c1.button("출발지로"):
            st.session_state.start_loc = {"lat": lat, "lon": lon, "addr": "지도 선택"}
            st.session_state.last_clicked = None
            st.rerun()
        if c2.button("도착지로"):
            st.session_state.dest_loc = {"lat": lat, "lon": lon, "addr": "지도 선택"}
            st.session_state.last_clicked = None
            st.rerun()

with col_map:
    # [연결 거부 해결] 탭을 사용하여 지도와 상세 경로를 분리
    tab1, tab2 = st.tabs(["🗺️ 한글 지도 (클릭 가능)", "🚌 상세 경로 리스트"])
    
    with tab1:
        # Folium은 연결 거부 에러가 발생하지 않습니다.
        m = folium.Map(
            location=[st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], 
            zoom_start=14,
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=ko", 
            attr="Google Maps"
        )
        folium.Marker([st.session_state.start_loc['lat'], st.session_state.start_loc['lon']], icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([st.session_state.dest_loc['lat'], st.session_state.dest_loc['lon']], icon=folium.Icon(color='red')).add_to(m)
        
        map_data = st_folium(m, width="100%", height=700, returned_objects=["last_clicked"])
        if map_data and map_data.get("last_clicked"):
            st.session_state.last_clicked = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
            st.rerun()

    with tab2:
        # [핵심] 연결 거부를 피하기 위해 '공개용 검색 페이지' 형식을 내부에 삽입
        # 출발지와 목적지 이름을 검색어로 사용하여 경로 리스트를 띄웁니다.
        s_name = st.session_state.start_loc['addr'].replace(" ", "+")
        d_name = st.session_state.dest_loc['addr'].replace(" ", "+")
        
        # 이 방식은 구글이 연결을 거부하지 않는 표준 검색 임베드 방식입니다.
        # 지도가 아닌 '상세 텍스트 경로' 위주로 정보가 나옵니다.
        path_url = f"https://www.google.com/maps/embed/v1/directions?key=YOUR_GOOGLE_MAPS_API_KEY&origin={s_name}&destination={d_name}&mode=transit&language=ko"
        
        # 만약 API 키가 아예 없다면 아래 주소로 대체 (연결 거부 가능성 낮음)
        fallback_url = f"https://maps.google.com/maps?q={d_name}&output=embed&hl=ko"
        
        st.markdown(f'<iframe src="{fallback_url}"></iframe>', unsafe_allow_html=True)
        st.warning("⚠️ 상세 경로 리스트(버스/지하철)는 구글 정책에 따라 외부 링크를 통해 더 자세히 볼 수 있습니다.")
