
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 외국인이 사랑하는 서울 관광지 TOP 10")
st.write("서울의 대표적인 관광 명소를 지도에서 확인해 보세요!")

# 관광지 데이터
places = [
    ("경복궁", 37.5796, 126.9770,
     "조선 왕조의 대표 궁궐로 한국의 전통 건축과 역사를 느낄 수 있는 곳입니다."),
    ("명동", 37.5636, 126.9869,
     "쇼핑, 화장품, 길거리 음식 등을 즐길 수 있는 서울의 대표 번화가입니다."),
    ("N서울타워", 37.5512, 126.9882,
     "남산에 위치한 전망대로 서울의 아름다운 전경을 감상할 수 있습니다."),
    ("북촌한옥마을", 37.5826, 126.9830,
     "전통 한옥이 모여 있어 한국의 옛 주거 문화를 경험할 수 있습니다."),
    ("인사동", 37.5740, 126.9855,
     "전통 공예품, 기념품, 전통 찻집 등을 만날 수 있는 문화 거리입니다."),
    ("홍대 거리", 37.5563, 126.9236,
     "개성 있는 카페와 쇼핑 거리, 거리 공연으로 유명한 곳입니다."),
    ("창덕궁", 37.5794, 126.9910,
     "자연과 조화를 이루는 아름다운 궁궐로 유네스코 세계유산입니다."),
    ("광장시장", 37.5700, 126.9998,
     "빈대떡과 다양한 한국 전통 음식을 맛볼 수 있는 전통 시장입니다."),
    ("동대문디자인플라자", 37.5671, 127.0095,
     "독특한 건축 디자인과 다양한 전시 및 문화 행사를 즐길 수 있습니다."),
    ("롯데월드", 37.5111, 127.0982,
     "다양한 놀이기구와 퍼레이드를 즐길 수 있는 대형 테마파크입니다.")
]

# 서울 지도 생성
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 관광지 마커 표시
for i, place in enumerate(places, 1):
    name, lat, lon, description = place

    folium.Marker(
        location=[lat, lon],
        tooltip=f"TOP {i} | {name}",
        popup=folium.Popup(
            f"<b>TOP {i}. {name}</b><br>{description}",
            max_width=300
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background-color:#2563eb;
                color:white;
                border-radius:50%;
                width:30px;
                height:30px;
                line-height:30px;
                text-align:center;
                font-weight:bold;
                border:2px solid white;
            ">{i}</div>
            """
        )
    ).add_to(m)

# 지도 출력
st.subheader("📍 서울 관광지 지도")

st_folium(
    m,
    width=None,
    height=550,
    use_container_width=True
)

# 관광지 설명
st.subheader("✨ 관광지 소개")

for i, place in enumerate(places, 1):
    name, lat, lon, description = place

    with st.expander(f"🏆 TOP {i}. {name}"):
        st.write(description)
        st.caption(f"위도: {lat} / 경도: {lon}")

st.divider()

st.caption(
    "※ 외국인 관광객에게 잘 알려진 서울의 대표 관광지 10곳을 선정했습니다. "
    "공식 실시간 방문객 순위는 아닙니다."
)
