
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------------------------
# 기본 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="Global MBTI",
    page_icon="🌎",
    layout="wide"
)

# ---------------------------------
# 데이터 불러오기
# ---------------------------------
@st.cache_data
def load_data():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "countriesMBTI_16types.csv"
    )

    df = pd.read_csv(file_path)

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. app.py와 같은 폴더에 CSV 파일을 넣어주세요.")
    st.stop()

# ---------------------------------
# 데이터 정리
# ---------------------------------
mbti_columns = [
    col for col in df.columns
    if col != "Country"
]

df["Country"] = df["Country"].astype(str).str.strip()

df[mbti_columns] = df[mbti_columns].apply(
    pd.to_numeric, errors="coerce"
)

df = df.dropna(subset=["Country"])

# 국가 이름 정렬
countries = sorted(df["Country"].unique())

# ---------------------------------
# 제목
# ---------------------------------
st.title("🌎 Global MBTI")
st.subheader("국가별 MBTI 유형 분포 분석")

st.write(
    "원하는 국가를 선택하면 해당 국가의 "
    "16가지 MBTI 유형별 비율을 확인할 수 있습니다."
)

st.divider()

# ---------------------------------
# 국가 선택
# ---------------------------------
selected_country = st.selectbox(
    "🌍 국가를 선택하세요",
    countries
)

# 선택한 국가 데이터
country_data = df[
    df["Country"] == selected_country
].iloc[0]

# ---------------------------------
# MBTI 데이터 정리
# ---------------------------------
chart_df = pd.DataFrame({
    "MBTI": mbti_columns,
    "비율": [
        country_data[mbti] * 100
        for mbti in mbti_columns
    ]
})

# 높은 비율 순서대로 정렬
chart_df = chart_df.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)

# ---------------------------------
# 그래프 색상 설정
# ---------------------------------
colors = []

for i in range(len(chart_df)):

    if i == 0:
        # 1위: 빨간색
        colors.append("#E53935")

    else:
        # 나머지: 초록색에서 연한 초록색으로
        progress = (i - 1) / max(len(chart_df) - 2, 1)

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
# 최고 비율 정보
# ---------------------------------
top_mbti = chart_df.iloc[0]["MBTI"]
top_ratio = chart_df.iloc[0]["비율"]

col1, col2, col3 = st.columns(3)

col1.metric("선택 국가", selected_country)
col2.metric("가장 높은 MBTI", top_mbti)
col3.metric("최고 비율", f"{top_ratio:.2f}%")

st.divider()

# ---------------------------------
# 막대 그래프
# ---------------------------------
st.subheader(f"📊 {selected_country} MBTI 비율")

fig = px.bar(
    chart_df,
    x="비율",
    y="MBTI",
    orientation="h",
    text="비율"
)

fig.update_traces(
    marker_color=colors,
    texttemplate="%{text:.2f}%",
    textposition="outside",
    hovertemplate=(
        "MBTI: %{y}<br>"
        "비율: %{x:.2f}%<extra></extra>"
    )
)

fig.update_layout(
    yaxis=dict(
        autorange="reversed",
        title="MBTI 유형"
    ),
    xaxis=dict(
        title="비율 (%)",
        rangemode="tozero"
    ),
    showlegend=False,
    height=650,
    margin=dict(l=40, r=60, t=30, b=40),
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
# 전체 데이터 표
# ---------------------------------
with st.expander("📋 MBTI 전체 비율 확인하기"):

    display_df = chart_df.copy()

    display_df["비율"] = display_df["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------
# 하단 설명
# ---------------------------------
st.divider()

st.caption(
    "Global MBTI | Country-based MBTI Distribution"
)

st.caption(
    "※ 본 데이터는 국가별 MBTI 유형 비율 자료이며, "
    "실제 국민 전체의 성격을 확정하는 자료는 아닙니다."
)
