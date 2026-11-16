
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write("붓꽃의 꽃받침과 꽃잎의 크기를 이용해 품종을 예측합니다.")


# --------------------------------------------------
# CSV 파일 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    current_dir = Path(__file__).resolve().parent

    file_paths = [
        current_dir / "Iris.csv",
        current_dir.parent / "Iris.csv"
    ]

    file_path = None

    for path in file_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        st.error("Iris.csv 파일을 찾을 수 없습니다. GitHub 저장소 위치를 확인해 주세요.")
        st.stop()

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        st.error("CSV 파일의 인코딩을 읽을 수 없습니다.")
        st.stop()

    return data


df = load_data()


# --------------------------------------------------
# 데이터 열 확인
# --------------------------------------------------
features = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비"
]

target = "품종"

missing_columns = [
    col for col in features + [target]
    if col not in df.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.write("현재 CSV 열 이름:", list(df.columns))
    st.stop()


X = df[features]
y = df[target]


# --------------------------------------------------
# 알고리즘 3개 생성
# --------------------------------------------------
def create_models():

    models = {
        "SVM": make_pipeline(
            StandardScaler(),
            SVC(kernel="rbf")
        ),

        "KNN": make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=5)
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
    }

    return models


# --------------------------------------------------
# 예측 페이지
# --------------------------------------------------
def prediction_page(selected_features):

    st.subheader("1. 측정값 입력")

    col1, col2 = st.columns(2)

    input_values = []

    for i, feature in enumerate(selected_features):

        minimum = float(df[feature].min())
        maximum = float(df[feature].max())
        median = float(df[feature].median())

        with [col1, col2][i]:
            value = st.slider(
                feature,
                min_value=minimum,
                max_value=maximum,
                value=median
            )

        input_values.append(value)

    input_data = pd.DataFrame(
        [input_values],
        columns=selected_features
    )

    st.write("입력한 측정값")
    st.dataframe(input_data, use_container_width=True)

    # 모델 학습
    models = create_models()

    for model in models.values():
        model.fit(X[selected_features], y)

    # --------------------------------------------------
    # 세 가지 알고리즘 예측 결과 비교
    # --------------------------------------------------
    st.subheader("2. 알고리즘별 품종 예측 결과")

    results = {}

    for name, model in models.items():
        results[name] = model.predict(input_data)[0]

    comparison = pd.DataFrame({
        "분류 알고리즘": list(results.keys()),
        "예측 품종": list(results.values())
    })

    st.write("### 알고리즘별 예측 비교")

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 품종별 예측 횟수
    # --------------------------------------------------
    st.write("### 품종별 예측 결과 비교")

    vote_counts = pd.Series(results).value_counts()

    vote_df = pd.DataFrame({
        "품종": vote_counts.index,
        "예측 횟수": vote_counts.values
    })

    st.bar_chart(
        vote_df.set_index("품종")
    )

    max_votes = vote_counts.max()
    winners = vote_counts[
        vote_counts == max_votes
    ].index.tolist()

    if len(winners) == 1:
        st.success(
            f"가장 많은 알고리즘이 예측한 품종: "
            f"{winners[0]} ({max_votes}/3)"
        )
    else:
        st.warning(
            "예측 결과가 동률입니다: "
            + ", ".join(map(str, winners))
        )

    if max_votes == 3:
        st.success("세 가지 알고리즘의 예측 결과가 모두 일치합니다!")
    elif max_votes == 2:
        st.info("세 가지 알고리즘 중 두 가지의 예측 결과가 일치합니다.")
    else:
        st.warning("세 가지 알고리즘의 예측 결과가 서로 다릅니다.")

    # --------------------------------------------------
    # 산점도
    # --------------------------------------------------
    st.subheader("3. 붓꽃 데이터 분포 그래프")

    fig, ax = plt.subplots(figsize=(9, 6))

    species_list = df[target].unique()

    for species in species_list:

        species_data = df[df[target] == species]

        ax.scatter(
            species_data[selected_features[0]],
            species_data[selected_features[1]],
            label=str(species),
            alpha=0.6
        )

    # 사용자가 입력한 값
    ax.scatter(
        input_values[0],
        input_values[1],
        color="green",
        marker="*",
        s=300,
        label="입력한 측정값",
        edgecolors="black"
    )

    ax.set_xlabel(selected_features[0])
    ax.set_ylabel(selected_features[1])
    ax.set_title("붓꽃 품종별 데이터 분포")
    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)

    # --------------------------------------------------
    # 알고리즘 작동 원리
    # --------------------------------------------------
    st.subheader("4. 분류 알고리즘 작동 원리")

    with st.expander("① SVM (서포트 벡터 머신)"):

        st.write("""
        SVM은 데이터를 가장 잘 구분할 수 있는 경계선을 찾는 알고리즘입니다.

        품종별 데이터 사이의 간격을 최대한 넓히는 방향으로
        분류 기준을 정합니다.
        """)

    with st.expander("② KNN (최근접 이웃)"):

        st.write("""
        KNN은 새로 입력한 데이터와 가까운 데이터 5개를 찾습니다.

        가까운 데이터들의 품종을 비교하여
        가장 많이 나타난 품종으로 예측합니다.
        """)

    with st.expander("③ Random Forest (랜덤 포레스트)"):

        st.write("""
        랜덤 포레스트는 여러 개의 의사결정나무를 만들어
        각각 품종을 예측하게 합니다.

        여러 나무의 예측 결과를 종합하여
        최종 품종을 결정합니다.
        """)


# --------------------------------------------------
# 탭 구성
# --------------------------------------------------
tab1, tab2 = st.tabs([
    "🌸 꽃잎으로 예측하기",
    "🔍 원하는 속성 2개로 예측하기"
])


with tab1:

    st.header("꽃잎 길이와 꽃잎 너비로 예측")

    prediction_page([
        "꽃잎 길이",
        "꽃잎 너비"
    ])


with tab2:

    st.header("원하는 속성 2개 선택하기")

    col1, col2 = st.columns(2)

    with col1:
        feature1 = st.selectbox(
            "첫 번째 속성",
            features,
            index=0
        )

    second_options = [
        feature for feature in features
        if feature != feature1
    ]

    with col2:
        feature2 = st.selectbox(
            "두 번째 속성",
            second_options,
            index=0
        )

    prediction_page([
        feature1,
        feature2
    ])
