
import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 제목
st.title("🗺️ 외국인이 사랑하는 서울 관광지 TOP 10")
st.markdown(
    "서울을 방문하는 외국인 관광객에게 인기 있는 "
    "대표 관광 명소 10곳을 소개합니다."
)

# 관광지 데이터
places = [
    {
        "name": "경복궁",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선 왕조의 대표 궁궐입니다. 아름다운 전통 건축과 한국의 역사를 경험할 수 있습니다."
    },
    {
        "name": "명동",
        "lat": 37.5636,
        "lon": 126.9869,
        "description": "화장품 쇼핑과 길거리 음식으로 유명한 서울의 대표 번화가입니다."
    },
    {
        "name": "N서울타워",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "남산에 위치한 전망대로 서울의 아름다운 도시 풍경을 감상할 수 있습니다."
    },
    {
        "name": "북촌한옥마을",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥이 모여 있는 곳으로 한국의 옛 주거 문화를 느낄 수 있습니다."
    },
    {
        "name": "인사동",
        "lat": 37.5740,
        "lon": 126.9855,
        "description": "전통 공예품과 기념품, 전통 찻집 등을 만날 수 있는 문화 거리입니다."
    },
    {
        "name": "홍대 거리",
        "lat": 37.5563,
        "lon": 126.9236,
        "description": "개성 있는 카페와 상점, 거리 공연으로 유명한 젊음의 거리입니다."
    },
    {
        "name": "창덕궁",
        "lat": 37.5794,
        "lon": 126.9910,
        "description": "자연 지형과 조화를 이루는 아름다운 궁궐이며 유네스코 세계유산입니다."
    },
    {
        "name": "광장시장",
        "lat": 37.5700,
        "lon": 126.9998,
        "description": "빈대떡과 다양한 한국 전통 음식을 맛볼 수 있는 전통 시장입니다."
    },
    {
        "name": "동대문디자인플라자",
        "lat": 37.5671,
        "lon": 127.0095,
        "description": "독특한 건축 디자인과 전시, 다양한 문화 행사를 즐길 수 있는 공간입니다."
    },
    {
        "name": "롯데월드",
        "lat": 37.5111,
        "lon": 127.0982,
        "description": "다양한 놀이기구와 퍼레이드를 즐길 수 있는 대형 테마파크입니다."
    }
]

# 지도 생성
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 관광지 마커 표시
for i, place in enumerate(places, start=1):

    popup_text = f"""
    <div style="width:220px">
        <h4>TOP {i}. {place['name']}</h4>
        <p>{place['description']}</p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"TOP {i} - {place['name']}",
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background-color:#2563eb;
                color:white;
                border-radius:50%;
                width:32px;
                height:32px;
                line-height:32px;
                text-align:center;
                font-weight:bold;
                border:2px solid white;
                box-shadow:0 2px 5px #888;
            ">
                {i}
            </div>
            """,
            icon_size=(32, 32),
            icon_anchor=(16, 16)
        )
    ).add_to(m)

# 지도 출력
st.subheader("📍 서울 관광지 위치")

st_folium(
    m,
    use_container_width=True,
    height=550,
    returned_objects=[]
)

# 관광지 설명
st.subheader("✨ 서울의 대표 관광지 TOP 10")

for i, place in enumerate(places, start=1):

    with st.container(border=True):
        st.markdown(f"### 🏆 TOP {i}. {place['name']}")
        st.write(place["description"])

st.divider()

st.info(
    "이 목록은 외국인 관광객에게 잘 알려진 "
    "서울의 대표 관광지를 선정한 참고용 목록입니다. "
    "공식 방문객 통계 순위는 아닙니다."
)

st.caption("Seoul Tourism TOP 10 | Made with Streamlit")
