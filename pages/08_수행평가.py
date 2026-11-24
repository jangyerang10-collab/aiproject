
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -------------------------
# 1. 기본 설정
# -------------------------

st.set_page_config(
    page_title="Sweet Data",
    page_icon="🍰",
    layout="wide"
)

st.title("🍰 Sweet Data")
st.subheader("음식 영양정보 분석 및 디저트 탐색")

st.write(
    "공공데이터를 활용하여 음식의 영양성분을 검색하고 분석하는 프로그램입니다."
)

# -------------------------

# -------------------------
# 2. 데이터 불러오기
# -------------------------

# GitHub 저장소에 업로드한 CSV 파일 자동 불러오기
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "전국통합식품영양성분정보_음식_표준데이터.csv"


@st.cache_data
def load_data(file):
    try:
        return pd.read_csv(file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(file, encoding="cp949")


if DATA_FILE.exists():
    df = load_data(DATA_FILE)
else:
    st.error("영양정보 CSV 파일을 찾을 수 없습니다.")
    st.stop()

df.columns = df.columns.astype(str).str.strip()

# -------------------------
# 3. 열 이름 자동 인식
# -------------------------

def find_column(keywords):
    for keyword in keywords:
        for col in df.columns:
            if keyword.lower() == col.lower():
                return col

    for keyword in keywords:
        for col in df.columns:
            if keyword.lower() in col.lower():
                return col

    return None


name_col = find_column(["음식명", "식품명", "메뉴명"])

energy_col = find_column(["에너지(kcal)", "에너지", "열량"])
sugar_col = find_column(["당류(g)", "당류"])
carb_col = find_column(["탄수화물(g)", "탄수화물"])
protein_col = find_column(["단백질(g)", "단백질"])
fat_col = find_column(["지방(g)", "지방"])


if name_col is None:
    st.error("음식명 열을 찾지 못했습니다.")
    st.write("현재 CSV 열 이름:", list(df.columns))
    st.stop()


nutrition = {
    "에너지(kcal)": energy_col,
    "당류(g)": sugar_col,
    "탄수화물(g)": carb_col,
    "단백질(g)": protein_col,
    "지방(g)": fat_col
}


# 영양성분 숫자 변환
for col in nutrition.values():
    if col:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )


df["_음식이름"] = df[name_col].astype(str).str.strip()

df = df[
    df["_음식이름"].ne("") &
    df["_음식이름"].ne("nan")
].copy()


# -------------------------
# 4. 메뉴 구성
# -------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 데이터 소개",
    "🔎 음식 검색",
    "📊 영양성분 그래프",
    "⚖️ 음식 비교",
    "📈 Pandas 분석"
])


# -------------------------
# 5. 데이터 소개
# -------------------------

with tab1:

    st.header("데이터 한눈에 보기")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "전체 음식 데이터",
        f"{len(df):,}개"
    )

    col2.metric(
        "전체 열 개수",
        f"{len(df.columns) - 1:,}개"
    )

    col3.metric(
        "중복 데이터",
        f"{df.duplicated().sum():,}개"
    )

    st.subheader("데이터 미리보기")

    st.dataframe(
        df.drop(columns=["_음식이름"]).head(20),
        use_container_width=True
    )

    st.caption(
        "출처: 공공데이터포털 전국통합식품영양성분정보(음식) 표준데이터"
    )


# -------------------------
# 6. 음식 검색
# -------------------------

with tab2:

    st.header("음식 영양정보 검색")

    keyword = st.text_input(
        "검색할 음식 이름을 입력하세요",
        placeholder="예: 케이크, 빵, 쿠키"
    )

    if keyword:
        result = df[
            df["_음식이름"].str.contains(
                keyword,
                case=False,
                na=False
            )
        ]
    else:
        result = df

    st.write(f"검색 결과: {len(result):,}개")

    show_cols = [name_col] + [
        col for col in nutrition.values() if col
    ]

    st.dataframe(
        result[show_cols].head(300),
        use_container_width=True
    )

    if not result.empty:

        selected = st.selectbox(
            "자세히 볼 음식 선택",
            result["_음식이름"].drop_duplicates().tolist()
        )

        item = result[
            result["_음식이름"] == selected
        ].iloc[0]

        st.subheader(selected)

        available = [
            (label, col)
            for label, col in nutrition.items()
            if col
        ]

        if available:

            cards = st.columns(len(available))

            for card, (label, col) in zip(cards, available):

                value = item[col]

                card.metric(
                    label,
                    "정보 없음"
                    if pd.isna(value)
                    else f"{value:g}"
                )


# -------------------------
# 7. 영양성분 그래프
# -------------------------

with tab3:

    st.header("영양성분 그래프 분석")

    available = {
        label: col
        for label, col in nutrition.items()
        if col
    }

    if available:

        selected_nutrient = st.selectbox(
            "분석할 영양성분 선택",
            list(available.keys())
        )

        selected_col = available[selected_nutrient]

        chart_df = (
            df[[name_col, selected_col]]
            .dropna()
            .nlargest(15, selected_col)
        )

        if not chart_df.empty:

            fig = px.bar(
                chart_df.sort_values(selected_col),
                x=selected_col,
                y=name_col,
                orientation="h",
                title=f"{selected_nutrient} 상위 15개 음식"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # 상관관계 분석
        if len(available) >= 2:

            st.subheader("영양성분 상관관계 분석")

            x_label = st.selectbox(
                "가로축 영양성분",
                list(available.keys()),
                index=0
            )

            y_label = st.selectbox(
                "세로축 영양성분",
                list(available.keys()),
                index=1
            )

            x_col = available[x_label]
            y_col = available[y_label]

            if x_col != y_col:

                scatter_df = df[
                    [name_col, x_col, y_col]
                ].dropna()

                fig2 = px.scatter(
                    scatter_df,
                    x=x_col,
                    y=y_col,
                    hover_name=name_col,
                    title=f"{x_label}과 {y_label}의 관계"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

                corr = scatter_df[x_col].corr(
                    scatter_df[y_col]
                )

                st.metric(
                    "피어슨 상관계수",
                    "계산 불가"
                    if pd.isna(corr)
                    else f"{corr:.3f}"
                )

                st.caption(
                    "상관관계는 두 항목의 변화 경향을 보여주며, "
                    "원인과 결과를 증명하지는 않습니다."
                )


# -------------------------
# 8. 음식 비교
# -------------------------

with tab4:

    st.header("음식 2개 영양성분 비교")

    choices = df["_음식이름"].drop_duplicates().tolist()

    if len(choices) >= 2:

        col1, col2 = st.columns(2)

        food_a = col1.selectbox(
            "첫 번째 음식",
            choices
        )

        food_b = col2.selectbox(
            "두 번째 음식",
            choices,
            index=1
        )

        row_a = df[
            df["_음식이름"] == food_a
        ].iloc[0]

        row_b = df[
            df["_음식이름"] == food_b
        ].iloc[0]

        compare_data = []

        for label, col in nutrition.items():

            if col:

                compare_data.append({
                    "영양성분": label,
                    food_a: row_a[col],
                    food_b: row_b[col]
                })

        if compare_data:

            compare_df = pd.DataFrame(compare_data)

            st.dataframe(
                compare_df,
                use_container_width=True
            )

            chart_df = compare_df.melt(
                id_vars="영양성분",
                var_name="음식",
                value_name="함량"
            )

            fig = px.bar(
                chart_df,
                x="영양성분",
                y="함량",
                color="음식",
                barmode="group",
                title="음식별 영양성분 비교"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.info("비교할 음식 데이터가 2개 이상 필요합니다.")


# -------------------------
# 9. Pandas 분석
# -------------------------

with tab5:

    st.header("Pandas 데이터 분석")

    st.subheader("① 데이터 기본 정보")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "행 개수",
        f"{df.shape[0]:,}"
    )

    col2.metric(
        "열 개수",
        f"{df.shape[1] - 1:,}"
    )

    col3.metric(
        "중복 행",
        f"{df.duplicated().sum():,}"
    )

    # 결측치 분석
    st.subheader("② 결측치 분석")

    missing = df.drop(
        columns=["_음식이름"]
    ).isnull().sum()

    missing_df = pd.DataFrame({
        "항목": missing.index,
        "결측치 개수": missing.values,
        "결측치 비율(%)": (
            missing.values / len(df) * 100
        ).round(2)
    })

    st.dataframe(
        missing_df,
        use_container_width=True
    )

    # 기초 통계
    st.subheader("③ 영양성분 기초 통계")

    numeric_cols = [
        col for col in nutrition.values() if col
    ]

    if numeric_cols:

        st.dataframe(
            df[numeric_cols].describe().T.round(2),
            use_container_width=True
        )

    # 분석 결과 다운로드
    st.subheader("④ 분석 데이터 다운로드")

    csv_data = df.drop(
        columns=["_음식이름"]
    ).to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        "📥 CSV 분석 결과 다운로드",
        csv_data,
        "sweet_data_analysis.csv",
        "text/csv"
    )


# -------------------------
# 10. 마무리
# -------------------------

st.divider()

st.caption(
    "Sweet Data | 공공데이터 기반 음식 영양정보 분석 프로그램"
)
