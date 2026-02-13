import streamlit as st
import requests

# 1. 웹 페이지 기본 설정
st.set_page_config(page_title="글로벌 이동 가이드", layout="wide", page_icon="🌍")

# 디자인을 위한 간단한 CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 실시간 교통 & 날씨 가이드")
st.write("본인의 API 키를 입력하고 목적지를 검색하면 전 세계 어디든 실시간 정보를 알려드립니다.")

# 2. 사이드바 API 설정
with st.sidebar:
    st.header("🔑 API 설정")
    google_key = st.text_input("Google Maps API Key", type="password")
    weather_key = st.text_input("OpenWeather API Key", type="password")
    st.info("입력한 키는 브라우저를 닫으면 저장되지 않습니다.")

# 3. 메인 입력창
destination = st.text_input("어디로 가시나요?", placeholder="예: Paris, 강남역, New York")

if st.button("실시간 정보 확인하기"):
    if not google_key or not weather_key:
        st.warning("먼저 왼쪽 사이드바에 두 가지 API 키를 모두 입력해주세요!")
    elif not destination:
        st.warning("목적지를 입력해주세요.")
    else:
        try:
            # A. 구글 지오코딩 API: 주소를 좌표로 변환
            geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={destination}&key={google_key}"
            geo_res = requests.get(geo_url).json()
            
            if geo_res['status'] != 'OK':
                st.error("목적지를 찾을 수 없습니다. 정확한 명칭을 입력해 주세요.")
            else:
                loc = geo_res['results'][0]['geometry']['location']
                lat, lon = loc['lat'], loc['lng']
                address = geo_res['results'][0]['formatted_address']

                # B. OpenWeather API: 날씨 가져오기
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_key}&units=metric&lang=kr"
                w_res = requests.get(weather_url).json()

                # C. 결과 출력
                st.success(f"📍 분석 완료: {address}")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📍 위치 정보")
                    st.write(f"**위도:** {lat}")
                    st.write(f"**경도:** {lon}")
                    st.write(f"**지역:** {w_res['name']}")

                with col2:
                    st.subheader("🌤️ 실시간 날씨")
                    temp = w_res['main']['temp']
                    desc = w_res['weather'][0]['description']
                    st.metric(label="현재 온도", value=f"{temp}°C", delta=desc)
                    
                    if "비" in desc or "눈" in desc:
                        st.warning("⚠️ 도착지에 비/눈 소식이 있습니다. 우산을 챙기세요!")
                    else:
                        st.success("✨ 이동하기 좋은 날씨입니다.")
                
        except Exception as e:
            st.error("오류가 발생했습니다. API 키가 유효한지 확인해주세요.")