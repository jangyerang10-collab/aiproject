
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------
# 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="Global MBTI",
    page_icon="🌎",
    layout="wide"
)

# ---------------------------------
# CSV 파일 경로
# ---------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "countriesMBTI_16types.csv"


# ---------------------------------
# 데이터 불러오기
# ---------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)


if not CSV_PATH.exists():
    st.error(f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}")
    st.stop()

df = load_data()

# ---------------------------------
# 데이터 정리
# ---------------------------------
mbti_columns = [
    col for col in df.columns
    if col != "Country"
]

df["Country"] = df["Country"].astype(str).str.strip()

df[mbti_columns] = df[mbti_columns].apply(
    pd.to_numeric,
    errors="coerce"
)

df = df.dropna(subset=["Country"])

# ---------------------------------
# 제목
# ---------------------------------
st.title("🌎 Global MBTI")
st.subheader("세계 국가별 MBTI 비율 순위")

st.write(
    "MBTI 유형을 선택하면 해당 유형의 비율이 "
    "높은 국가부터 순서대로 확인할 수 있습니다."
)

st.divider()

# ---------------------------------
# MBTI 선택
# ---------------------------------
selected_mbti = st.selectbox(
    "🧬 MBTI 유형을 선택하세요",
    mbti_columns
)

# ---------------------------------
# 국가별 비율 정리
# ---------------------------------
chart_df = pd.DataFrame({
    "Country": df["Country"],
    "비율": df[selected_mbti] * 100
})

chart_df = chart_df.dropna(subset=["비율"])

# 높은 비율부터 정렬
chart_df = chart_df.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)

# 순위 추가
chart_df.insert(
    0,
    "순위",
    range(1, len(chart_df) + 1)
)

# ---------------------------------
# 그래프 표시 개수 선택
# ---------------------------------
display_option = st.selectbox(
    "📊 그래프에 표시할 국가 수",
    ["TOP 10", "TOP 20", "TOP 50", "전체 국가"],
    index=1
)

if display_option == "TOP 10":
    display_df = chart_df.head(10)

elif display_option == "TOP 20":
    display_df = chart_df.head(20)

elif display_option == "TOP 50":
    display_df = chart_df.head(50)

else:
    display_df = chart_df.copy()

# ---------------------------------
# 최고 비율 정보
# ---------------------------------
top_country = chart_df.iloc[0]["Country"]
top_ratio = chart_df.iloc[0]["비율"]

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택한 MBTI",
    selected_mbti
)

col2.metric(
    "1위 국가",
    top_country
)

col3.metric(
    "1위 비율",
    f"{top_ratio:.2f}%"
)

st.divider()

# ---------------------------------
# 그래프 색상 설정
# ---------------------------------
colors = []

for i in range(len(display_df)):

    if i == 0:
        colors.append("#E53935")

    else:
        progress = (i - 1) / max(len(display_df) - 2, 1)

        start_color = (46, 125, 50)
        end_color = (232, 245, 233)

        r = int(
            start_color[0] +
            (end_color[0] - start_color[0]) * progress
        )

        g = int(
            start_color[1] +
            (end_color[1] - start_color[1]) * progress
        )

        b = int(
            start_color[2] +
            (end_color[2] - start_color[2]) * progress
        )

        colors.append(f"rgb({r},{g},{b})")

# ---------------------------------
# 국가별 막대그래프
# ---------------------------------
st.subheader(
    f"📊 {selected_mbti} 국가별 비율 순위"
)

fig = px.bar(
    display_df,
    x="비율",
    y="Country",
    orientation="h",
    text="비율",
    custom_data=["순위"]
)

fig.update_traces(
    marker_color=colors,
    texttemplate="%{text:.2f}%",
    textposition="outside",
    hovertemplate=(
        "순위: %{customdata[0]}위<br>"
        "국가: %{y}<br>"
        "비율: %{x:.2f}%<extra></extra>"
    )
)

fig.update_layout(
    yaxis=dict(
        autorange="reversed",
        title="국가"
    ),

    xaxis=dict(
        title="비율 (%)",
        rangemode="tozero"
    ),

    showlegend=False,

    height=max(500, len(display_df) * 32),

    margin=dict(
        l=40,
        r=70,
        t=30,
        b=40
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Arial",
        size=13,
        color="#333333"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------
# 국가별 순위표
# ---------------------------------
with st.expander("🏆 국가별 전체 순위표"):

    result_df = chart_df.copy()

    result_df["비율"] = result_df["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------
# 하단 설명
# ---------------------------------
st.divider()

st.caption(
    "Global MBTI | World MBTI Ranking"
)

st.caption(
    "※ 본 데이터는 국가별 MBTI 유형 비율 자료이며, "
    "실제 국민 전체의 성격을 확정하는 자료는 아닙니다."
)
