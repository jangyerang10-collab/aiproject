
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# 페이지 설정
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 붓꽃의 품종을 예측합니다.")

# CSV 데이터 불러오기
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "Iris.csv"

    try:
        data = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="utf-8-sig")

    return data

df = load_data()

# 학습 데이터 설정
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# SVM 분류 모델 생성
model = make_pipeline(
    StandardScaler(),
    SVC(kernel="rbf", C=1.0, gamma="scale")
)

# 모델 학습
model.fit(X, y)

# 입력값 범위 설정
length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

# 사용자 입력
st.subheader("1. 꽃잎 정보 입력")

st.write(
    f"꽃잎 길이: {length_min} ~ {length_max} cm"
)
st.write(
    f"꽃잎 너비: {width_min} ~ {width_max} cm"
)

col1, col2 = st.columns(2)

with col1:
    petal_length = st.slider(
        "꽃잎 길이 (cm)",
        length_min,
        length_max,
        1.0,
        step=0.1
    )

with col2:
    petal_width = st.slider(
        "꽃잎 너비 (cm)",
        width_min,
        width_max,
        0.1,
        step=0.1
    )

# 품종 예측
input_data = pd.DataFrame({
    "꽃잎 길이": [petal_length],
    "꽃잎 너비": [petal_width]
})

prediction = model.predict(input_data)[0]

# 예측 결과 출력
st.subheader("2. 품종 예측 결과")

st.success(f"예측된 붓꽃 품종: {prediction}")

st.write(f"꽃잎 길이: {petal_length} cm")
st.write(f"꽃잎 너비: {petal_width} cm")

# 그래프 출력
st.subheader("3. 꽃잎 크기 그래프")

fig, ax = plt.subplots(figsize=(9, 6))

# 기존 붓꽃 데이터 표시
for species in sorted(df["품종"].unique()):
    species_data = df[df["품종"] == species]

    ax.scatter(
        species_data["꽃잎 길이"],
        species_data["꽃잎 너비"],
        label=species,
        alpha=0.7
    )

# 사용자 입력값을 초록색 별로 표시
ax.scatter(
    petal_length,
    petal_width,
    color="green",
    marker="*",
    s=350,
    edgecolors="black",
    label="사용자 입력값",
    zorder=5
)

# 그래프 제목과 축 설정
ax.set_title("붓꽃 품종별 꽃잎 크기")
ax.set_xlabel("꽃잎 길이 (cm)")
ax.set_ylabel("꽃잎 너비 (cm)")

ax.legend()
ax.grid(alpha=0.25)

st.pyplot(fig)
plt.close(fig)

st.caption("초록색 별(★)은 사용자가 입력한 값입니다.")

# 알고리즘 설명
with st.expander("분석 및 알고리즘 설명"):
    st.write("사용한 알고리즘: 서포트 벡터 머신(SVM)")
    st.write("커널: RBF")
    st.write("입력 변수: 꽃잎 길이, 꽃잎 너비")
    st.write(f"전체 데이터 개수: {len(df)}개")
    st.write("모델 학습 후 입력값을 이용해 품종을 예측합니다.")
