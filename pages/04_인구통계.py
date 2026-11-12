
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from pathlib import Path

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="서울시 인구 분석",
    page_icon="🌸",
    layout="wide"
)

# -----------------------------
# 디자인
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #FFF8FC;
}

h1, h2, h3, p, label {
    color: #333333;
}

div.stButton > button {
    background-color: #FF1493;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CSV 파일 경로
# pages 폴더의 상위 폴더
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "popultion.csv"

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():

    try:
        df = pd.read_csv(
            CSV_PATH,
            encoding="euc-kr"
        )

    except UnicodeDecodeError:
        df = pd.read_csv(
            CSV_PATH,
            encoding="cp949"
        )

    # 지역명 정리
    df["지역명"] = (
        df["행정구역"]
        .astype(str)
        .str.replace("서울특별시", "", regex=False)
        .str.replace(r"\(\d+\)", "", regex=True)
        .str.strip()
    )

    df.loc[0, "지역명"] = "서울특별시"

    # 숫자 데이터 변환
    for col in df.columns:
        if col not in ["행정구역", "지역명"]:
            df[col] = pd.to_numeric(
                df[col].astype(str)
                .str.replace(",", "", regex=False),
                errors="coerce"
            )

    return df


# 데이터 실행
try:
    df = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. 상위 폴더에 popultion.csv가 있는지 확인하세요.")
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# -----------------------------
# 제목
# -----------------------------
st.title("🌸 서울시 인구 통계 분석")
st.caption("2020년 ~ 2025년 서울특별시 인구 데이터")

st.divider()


# -----------------------------
# 선택 메뉴
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    district = st.selectbox(
        "🏙️ 행정구역 선택",
        df["지역명"].tolist()
    )

with col2:
    gender = st.selectbox(
        "👥 성별 선택",
        ["전체", "남자", "여자"]
    )

with col3:
    year = st.selectbox(
        "📅 연도 선택",
        [2020, 2021, 2022, 2023, 2024, 2025],
        index=5
    )


st.divider()


# -----------------------------
# 선택 데이터
# -----------------------------
selected = df[df["지역명"] == district].iloc[0]

if gender == "남자":
    value_col = f"{year}년_남자 인구수"

elif gender == "여자":
    value_col = f"{year}년_여자 인구수"

else:
    value_col = f"{year}년_총인구수"

population = selected[value_col]


# -----------------------------
# 인구 정보
# -----------------------------
st.subheader("📊 선택 지역 인구 현황")

m1, m2 = st.columns(2)

with m1:
    st.metric(
        "선택한 인구수",
        f"{population:,.0f}명"
    )

with m2:
    st.metric(
        "선택 지역",
        district
    )


st.divider()


# -----------------------------
# 연령별 데이터 확인
# -----------------------------
age_columns = [
    c for c in df.columns
    if re.search(r"(\d+)\s*세", c)
]

if age_columns:

    st.subheader("📈 연령별 인구 꺾은선 그래프")

    age_data = []

    for col in age_columns:

        age_match = re.search(r"(\d+)\s*세", col)

        if not age_match:
            continue

        age = int(age_match.group(1))

        if gender == "남자" and "남자" not in col:
            continue

        elif gender == "여자" and "여자" not in col:
            continue

        age_data.append({
            "나이": age,
            "인구수": selected[col]
        })

    if age_data:

        chart_df = pd.DataFrame(age_data)
        chart_df = chart_df.sort_values("나이")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=chart_df["나이"],
                y=chart_df["인구수"],
                mode="lines+markers",
                line=dict(
                    color="#FF1493",
                    width=3
                ),
                marker=dict(
                    color="#FF1493",
                    size=7
                ),
                name="인구수"
            )
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="#FFF8FC",

            font=dict(
                family="sans-serif",
                color="#333333"
            ),

            xaxis=dict(
                title="나이",
                dtick=10,
                showgrid=True,
                gridcolor="#E8DCE3"
            ),

            yaxis=dict(
                title="인구수 (명)",
                dtick=100,
                rangemode="tozero",
                showgrid=True,
                gridcolor="#E8DCE3"
            ),

            hovermode="x unified",
            margin=dict(
                l=30,
                r=30,
                t=30,
                b=30
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.warning("선택한 성별에 해당하는 연령별 데이터가 없습니다.")

else:

    st.warning(
        "현재 CSV 파일에는 연령별 인구 데이터가 없습니다. "
        "연령별 인구가 포함된 파일이 필요합니다."
    )


# -----------------------------
# 원본 데이터 확인
# -----------------------------
with st.expander("📋 원본 인구 데이터 확인"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
