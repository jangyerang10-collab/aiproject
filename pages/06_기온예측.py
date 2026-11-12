
# ==========================================
# 1. 라이브러리 불러오기
# ==========================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor


# ==========================================
# 2. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 프로그램")

st.write(
    "다양한 회귀 알고리즘을 이용하여 "
    "선택한 월의 미래 평균기온을 예측합니다."
)

st.divider()


# ==========================================
# 3. CSV 파일 경로 설정
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "temperature.csv"

if not CSV_PATH.exists():
    CSV_PATH = BASE_DIR / "temperature(1).csv"


# ==========================================
# 4. CSV 파일 불러오기
# ==========================================
try:
    try:
        df = pd.read_csv(
            CSV_PATH,
            encoding="cp949"
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            CSV_PATH,
            encoding="utf-8-sig"
        )

except FileNotFoundError:
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.stop()

except Exception as e:
    st.error(f"CSV 파일 오류: {e}")
    st.stop()


# ==========================================
# 5. 데이터 전처리
# ==========================================
required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해주세요.")
    st.stop()

df["일시"] = pd.to_datetime(
    df["일시"],
    format="%b-%y",
    errors="coerce"
)

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["일시", "평균기온(℃)"]
).copy()

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

if df.empty:
    st.error("분석할 기온 데이터가 없습니다.")
    st.stop()


# ==========================================
# 6. 월 이름 설정
# ==========================================
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}


# ==========================================
# 7. 사용자 입력
# ==========================================
st.subheader("📌 예측 조건 설정")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    selected_algorithm = st.selectbox(
        "사용할 회귀 알고리즘",
        [
            "선형회귀",
            "다항회귀",
            "랜덤 포레스트 회귀"
        ]
    )


# 선택한 월의 데이터 추출
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.error("예측에 필요한 데이터가 부족합니다.")
    st.stop()

latest_year = int(month_df["연도"].max())

forecast_year = st.number_input(
    "예측할 연도",
    min_value=latest_year + 1,
    max_value=2100,
    value=latest_year + 1,
    step=1
)

forecast_year = int(forecast_year)

st.divider()


# ==========================================
# 8. 학습 데이터 설정
# ==========================================
X = month_df[["연도"]].values

y = month_df["평균기온(℃)"].values

X_future = np.array([[forecast_year]])


# ==========================================
# 9. 선형회귀 모델
# ==========================================
linear_model = LinearRegression()

linear_model.fit(X, y)

linear_prediction = linear_model.predict(
    X_future
)[0]


# ==========================================
# 10. 다항회귀 모델
# ==========================================
poly_features = PolynomialFeatures(
    degree=2
)

X_poly = poly_features.fit_transform(X)

X_future_poly = poly_features.transform(
    X_future
)

poly_model = LinearRegression()

poly_model.fit(X_poly, y)

poly_prediction = poly_model.predict(
    X_future_poly
)[0]


# ==========================================
# 11. 랜덤 포레스트 회귀 모델
# ==========================================
forest_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=4,
    min_samples_leaf=2,
    random_state=42
)

forest_model.fit(X, y)

forest_prediction = forest_model.predict(
    X_future
)[0]


# ==========================================
# 12. 예측 결과 저장
# ==========================================
predictions = {
    "선형회귀": linear_prediction,
    "다항회귀": poly_prediction,
    "랜덤 포레스트 회귀": forest_prediction
}

selected_prediction = predictions[
    selected_algorithm
]


# ==========================================
# 13. 예측 결과 출력
# ==========================================
st.subheader(
    f"📊 {month_names[selected_month]} 평균기온 예측 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선택한 알고리즘",
        selected_algorithm
    )

with col2:
    st.metric(
        "예측 연도",
        f"{forecast_year}년"
    )

with col3:
    st.metric(
        "예측 평균기온",
        f"{selected_prediction:.2f} ℃"
    )


# ==========================================
# 14. 세 가지 알고리즘 비교
# ==========================================
st.subheader("🔍 회귀 알고리즘별 예측값 비교")

comparison_df = pd.DataFrame({
    "회귀 알고리즘": list(predictions.keys()),
    "예측 평균기온(℃)": [
        round(value, 2)
        for value in predictions.values()
    ]
})

comparison_df["선택 여부"] = [
    "⭐ 선택됨" if name == selected_algorithm else ""
    for name in comparison_df["회귀 알고리즘"]
]

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 15. 그래프 데이터 생성
# ==========================================
graph_years = np.linspace(
    month_df["연도"].min(),
    forecast_year,
    300
).reshape(-1, 1)


# 선형회귀 그래프
linear_graph = linear_model.predict(
    graph_years
)


# 다항회귀 그래프
poly_graph = poly_model.predict(
    poly_features.transform(graph_years)
)


# 랜덤 포레스트 그래프
forest_graph = forest_model.predict(
    graph_years
)


# ==========================================
# 16. 그래프 그리기
# ==========================================
st.subheader("📈 실제 기온 및 알고리즘별 예측 그래프")

fig, ax = plt.subplots(figsize=(13, 7))


# 실제 데이터
ax.scatter(
    month_df["연도"],
    month_df["평균기온(℃)"],
    color="royalblue",
    s=55,
    label="Actual Temperature",
    zorder=5
)


# 알고리즘별 회귀 그래프
model_graphs = {
    "선형회귀": linear_graph,
    "다항회귀": poly_graph,
    "랜덤 포레스트 회귀": forest_graph
}

model_colors = {
    "선형회귀": "red",
    "다항회귀": "green",
    "랜덤 포레스트 회귀": "purple"
}

for name, graph_values in model_graphs.items():

    is_selected = name == selected_algorithm

    ax.plot(
        graph_years.ravel(),
        graph_values,
        color=model_colors[name],
        linewidth=3 if is_selected else 1.8,
        linestyle="-" if is_selected else "--",
        alpha=1 if is_selected else 0.65,
        label=(
            f"{name} (선택)"
            if is_selected
            else name
        )
    )


# 미래 예측값 표시
for name, value in predictions.items():

    is_selected = name == selected_algorithm

    ax.scatter(
        forecast_year,
        value,
        color=model_colors[name],
        s=180 if is_selected else 90,
        marker="*" if is_selected else "o",
        edgecolor="black",
        linewidth=0.8,
        zorder=10,
        label=f"{name} 예측값"
    )

    ax.annotate(
        f"{value:.1f}℃",
        (forecast_year, value),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=9
    )


# 그래프 설정
ax.set_title(
    f"{month_names[selected_month]} Average Temperature Prediction",
    fontsize=16
)

ax.set_xlabel("Year", fontsize=12)

ax.set_ylabel(
    "Average Temperature (℃)",
    fontsize=12
)

ax.grid(alpha=0.3)

ax.legend(
    loc="best",
    fontsize=9
)

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ==========================================
# 17. 알고리즘 설명
# ==========================================
st.divider()

st.subheader("🧠 회귀 알고리즘 알아보기")

st.markdown("""
### ① 선형회귀 (Linear Regression)

과거 데이터의 전체적인 변화 추세를 직선으로 나타내는 알고리즘입니다.

- 직선을 이용하여 기온을 예측합니다.
- 계산이 간단하고 결과를 이해하기 쉽습니다.
- 기온 변화가 직선적인 경향을 보일 때 활용하기 좋습니다.

### ② 다항회귀 (Polynomial Regression)

데이터의 변화 추세를 곡선으로 표현하는 알고리즘입니다.

- 직선뿐 아니라 곡선 형태의 패턴도 학습할 수 있습니다.
- 기온의 상승과 하락 추세를 표현할 수 있습니다.
- 이 프로그램에서는 2차 다항식을 사용합니다.

### ③ 랜덤 포레스트 회귀 (Random Forest Regression)

여러 개의 의사결정나무를 만들어 예측 결과를 결합하는 알고리즘입니다.

- 여러 나무의 예측 결과를 평균하여 최종 결과를 만듭니다.
- 복잡하고 비선형적인 데이터 패턴을 학습할 수 있습니다.
- 학습 데이터의 범위를 크게 벗어난 미래 연도에서는 예측값이 일정하게 유지되는 경향이 있습니다.
""")


# ==========================================
# 18. 알고리즘별 차이점
# ==========================================
st.divider()

st.subheader("⚖️ 알고리즘별 특징 비교")

feature_df = pd.DataFrame({
    "알고리즘": [
        "선형회귀",
        "다항회귀",
        "랜덤 포레스트 회귀"
    ],
    "그래프 형태": [
        "직선",
        "곡선",
        "계단 형태의 비선형 곡선"
    ],
    "특징": [
        "전체적인 직선 추세 학습",
        "곡선 형태의 변화 학습",
        "여러 의사결정나무 결합"
    ],
    "주의사항": [
        "곡선 패턴 표현에 한계",
        "차수가 높으면 과적합 가능",
        "미래 범위 밖 예측에 한계"
    ]
})

st.dataframe(
    feature_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 19. 최종 안내
# ==========================================
st.divider()

st.info(
    "같은 월과 같은 과거 데이터를 사용하더라도 "
    "회귀 알고리즘의 학습 방식이 다르기 때문에 "
    "예측 결과가 서로 다르게 나타날 수 있습니다."
)

st.caption(
    "데이터 출처: temperature.csv | "
    "사용 알고리즘: Linear Regression, "
    "Polynomial Regression, Random Forest Regression"
)
