
# ==============================
# 1. 라이브러리 불러오기
# ==============================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from pathlib import Path


# ==============================
# 2. 페이지 설정
# ==============================
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)


# ==============================
# 3. 제목
# ==============================
st.title("🌡️ 월별 평균기온 예측 프로그램")

st.write(
    "선형회귀 알고리즘을 이용하여 "
    "선택한 월의 미래 평균기온을 예측합니다."
)

st.divider()


# ==============================
# 4. CSV 파일 경로 설정
# ==============================
# 현재 PY 파일: pages/06_기온예측.py
# CSV 파일: 프로젝트 상위 폴더/temperature.csv

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "temperature.csv"

# temperature.csv가 없으면 원본 파일명도 확인
if not CSV_PATH.exists():
    CSV_PATH = BASE_DIR / "temperature(1).csv"


# ==============================
# 5. CSV 파일 불러오기
# ==============================
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
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "프로젝트 상위 폴더에 temperature.csv를 넣어주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"CSV 파일 오류: {e}")
    st.stop()


# ==============================
# 6. 데이터 전처리
# ==============================
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
    st.error("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()


# ==============================
# 7. 월 이름 설정
# ==============================
month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}


# ==============================
# 8. 사용자 입력
# ==============================
st.subheader("📌 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요.",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

# 선택한 월의 데이터만 추출
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("예측에 필요한 데이터가 부족합니다.")
    st.stop()

latest_year = int(month_df["연도"].max())

with col2:
    forecast_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=latest_year + 1,
        max_value=2100,
        value=latest_year + 1,
        step=1
    )

forecast_year = int(forecast_year)

st.divider()


# ==============================
# 9. 선형회귀 모델 학습
# ==============================
X = month_df[["연도"]]

y = month_df["평균기온(℃)"]

model = LinearRegression()

model.fit(X, y)


# ==============================
# 10. 미래 기온 예측
# ==============================
prediction = model.predict(
    pd.DataFrame({
        "연도": [forecast_year]
    })
)[0]


# 회귀 직선에 사용할 연도 생성
graph_years = np.linspace(
    month_df["연도"].min(),
    forecast_year,
    200
)

graph_temps = model.predict(
    pd.DataFrame({
        "연도": graph_years
    })
)


# ==============================
# 11. 예측 결과 출력
# ==============================
st.subheader(
    f"📊 {month_names[selected_month]} 평균기온 예측 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "예측 연도",
        f"{forecast_year}년"
    )

with col2:
    st.metric(
        "예측 평균기온",
        f"{prediction:.1f} ℃"
    )

with col3:
    st.metric(
        "학습 데이터 개수",
        f"{len(month_df)}개"
    )


# ==============================
# 12. 그래프 그리기
# ==============================
st.subheader("📈 실제 기온과 예측 기온 그래프")

fig, ax = plt.subplots(figsize=(12, 6))


# 실제 기온 데이터
ax.scatter(
    month_df["연도"],
    month_df["평균기온(℃)"],
    color="royalblue",
    s=50,
    label="Actual Temperature",
    zorder=3
)


# 실제 데이터와 회귀 직선 사이의 오차
for _, row in month_df.iterrows():

    fitted = model.predict(
        pd.DataFrame({
            "연도": [row["연도"]]
        })
    )[0]

    ax.plot(
        [row["연도"], row["연도"]],
        [row["평균기온(℃)"], fitted],
        color="gray",
        linestyle=":",
        alpha=0.4
    )


# 선형회귀 직선
ax.plot(
    graph_years,
    graph_temps,
    color="red",
    linewidth=2.5,
    label="Linear Regression"
)


# 미래 예측 기온
ax.scatter(
    forecast_year,
    prediction,
    color="orange",
    edgecolor="black",
    s=180,
    marker="*",
    label="Predicted Temperature",
    zorder=5
)


# 예측값 표시
ax.annotate(
    f"{prediction:.1f}℃",
    (forecast_year, prediction),
    xytext=(10, 12),
    textcoords="offset points",
    fontsize=12,
    color="darkorange",
    fontweight="bold"
)


# 그래프 설정
ax.set_title(
    f"{month_names[selected_month]} Average Temperature Prediction",
    fontsize=15
)

ax.set_xlabel(
    "Year",
    fontsize=12
)

ax.set_ylabel(
    "Average Temperature (℃)",
    fontsize=12
)

ax.grid(
    alpha=0.3
)

ax.legend()

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ==============================
# 13. 선형회귀 분석 결과
# ==============================
st.divider()

st.subheader("🧠 선형회귀 알고리즘 분석")

slope = model.coef_[0]

intercept = model.intercept_

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "회귀 직선의 기울기",
        f"{slope:.4f}"
    )

with col2:
    st.metric(
        "회귀 직선의 절편",
        f"{intercept:.2f}"
    )


# 선형회귀 수식
st.write("### 선형회귀 수식")

st.latex(
    rf"y = {slope:.4f}x + ({intercept:.2f})"
)


# ==============================
# 14. 선형회귀 알고리즘 설명
# ==============================
st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.write("""
선형회귀는 과거 데이터를 분석하여
두 변수 사이의 관계를 직선으로 나타내고,
그 직선을 이용하여 미래의 값을 예측하는
머신러닝 알고리즘입니다.
""")

st.write("### ① 데이터 수집")

st.write("""
CSV 파일에서 선택한 월의 연도별 평균기온 데이터를 가져옵니다.

연도는 X값, 평균기온은 Y값으로 사용합니다.
""")

st.write("### ② 데이터 학습")

st.write("""
선형회귀 알고리즘이 과거의 연도별 기온 데이터를 분석합니다.

데이터의 전체적인 변화 추세를 파악합니다.
""")

st.write("### ③ 회귀 직선 생성")

st.write("""
실제 데이터와 직선 사이의 오차 제곱합이
가장 작아지는 직선을 찾습니다.

이 직선이 그래프의 빨간색 선입니다.
""")

st.write("### ④ 미래 기온 예측")

st.write("""
학습이 끝나면 사용자가 입력한 예측연도를
회귀 직선에 적용하여 미래의 평균기온을 계산합니다.

그래프의 주황색 별이 예측된 기온입니다.
""")

st.divider()

st.subheader("🎨 그래프 색상 설명")

st.write("""
🔵 파란색 점 : 과거의 실제 평균기온

🔴 빨간색 선 : 선형회귀 알고리즘이 학습한 직선

🟠 주황색 별 : 미래의 예측 평균기온

회색 점선 : 실제 기온과 회귀 직선 사이의 오차(잔차)
""")

st.divider()

st.subheader("⚖️ 선형회귀 알고리즘의 장점과 한계")

st.write("""
**장점**

- 계산 과정이 간단하고 이해하기 쉽습니다.
- 과거 데이터의 변화 추세를 확인할 수 있습니다.
- 새로운 연도의 기온을 예측할 수 있습니다.

**한계**

- 기온에 영향을 주는 다양한 기상 요인을 반영하지 못합니다.
- 과거의 변화 추세가 미래에도 이어진다고 가정합니다.
- 예측 기간이 길어질수록 실제 기온과 차이가 커질 수 있습니다.
""")

st.divider()

st.caption(
    "데이터 출처: temperature.csv | "
    "예측 알고리즘: Scikit-learn LinearRegression"
)
