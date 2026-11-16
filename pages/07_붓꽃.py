
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier


# 페이지 설정
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write("꽃의 특징을 입력하여 붓꽃의 품종을 예측해 보세요.")


# CSV 데이터 불러오기
@st.cache_data
def load_data():
    current_dir = Path(__file__).resolve().parent

    paths = [
        current_dir / "Iris.csv",
        current_dir.parent / "Iris.csv"
    ]

    csv_path = next(
        (p for p in paths if p.is_file()),
        None
    )

    if csv_path is None:
        st.error("Iris.csv 파일을 찾을 수 없습니다.")
        st.stop()

    data = None

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            data = pd.read_csv(
                csv_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if data is None:
        st.error("CSV 파일을 읽을 수 없습니다.")
        st.stop()

    return data


df = load_data()


# 사용할 속성
features = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비"
]

target = "품종"

# 모델 3가지 생성
def create_models():

    models = {
        "SVM": make_pipeline(
            StandardScaler(),
            SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale"
            )
        ),

        "KNN": make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(
                n_neighbors=5
            )
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
    }

    return models


# 예측 및 그래프 출력 함수
def prediction_page(selected_features):

    # 학습 데이터
    X = df[selected_features]
    y = df[target]

    # 모델 생성
    models = create_models()

    for model in models.values():
        model.fit(X, y)

    # 입력 범위 설정
    st.subheader("꽃의 특징 입력")

    col1, col2 = st.columns(2)

    input_values = []

    for i, feature in enumerate(selected_features):

        min_value = float(df[feature].min())
        max_value = float(df[feature].max())

        default_value = round(
            float(df[feature].median()), 1
        )

        with [col1, col2][i]:
            value = st.slider(
                feature + " (cm)",
                min_value=min_value,
                max_value=max_value,
                value=default_value,
                step=0.1,
                key="input_" + feature
            )

        input_values.append(value)

    # 입력값 데이터프레임
    input_data = pd.DataFrame(
        [input_values],
        columns=selected_features
    )

    # 예측 결과
    st.subheader("품종 예측 결과")

    result_columns = st.columns(3)

    for i, (name, model) in enumerate(models.items()):

        result = model.predict(input_data)[0]

        with result_columns[i]:
            st.metric(
                label=name,
                value=result
            )

    # 그래프
    st.subheader("입력값 그래프")

    fig, ax = plt.subplots(figsize=(9, 6))

    # 기존 데이터 표시
    for species in sorted(df[target].unique()):

        species_data = df[df[target] == species]

        ax.scatter(
            species_data[selected_features[0]],
            species_data[selected_features[1]],
            label=species,
            alpha=0.7
        )

    # 사용자 입력값 초록색 별 표시
    ax.scatter(
        input_values[0],
        input_values[1],
        color="green",
        marker="*",
        s=350,
        edgecolors="black",
        linewidths=0.7,
        label="사용자 입력값",
        zorder=5
    )

    ax.set_xlabel(selected_features[0] + " (cm)")
    ax.set_ylabel(selected_features[1] + " (cm)")
    ax.set_title("붓꽃 품종별 특징 비교")

    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)

    st.caption("초록색 별(★)은 사용자가 입력한 값입니다.")

    # 알고리즘 작동 원리
    st.divider()
    st.subheader("알고리즘별 작동 원리")

    with st.expander("1. SVM (서포트 벡터 머신)"):
        st.write(
            """
            SVM은 데이터를 가장 잘 구분하는 경계선을 찾는
            분류 알고리즘입니다.

            서로 다른 품종의 데이터 사이에 가장 적절한
            경계를 만들어 새로운 꽃의 품종을 예측합니다.

            RBF 커널을 사용하여 직선으로 구분하기 어려운
            데이터도 분류할 수 있습니다.
            """
        )

    with st.expander("2. KNN (최근접 이웃 알고리즘)"):
        st.write(
            """
            KNN은 새로운 데이터와 가까운 기존 데이터들을
            찾아 품종을 예측하는 알고리즘입니다.

            이번 프로그램에서는 가장 가까운 5개의 데이터를
            확인하고, 가장 많이 나타나는 품종으로 예측합니다.
            """
        )

    with st.expander("3. Random Forest (랜덤 포레스트)"):
        st.write(
            """
            랜덤 포레스트는 여러 개의 의사결정나무를 만들어
            결과를 종합하는 분류 알고리즘입니다.

            각각의 나무가 꽃의 특징을 분석하고,
            여러 나무의 예측 결과를 모아 가장 많이 선택된
            품종을 최종 결과로 결정합니다.
            """
        )


# 탭 만들기
tab1, tab2 = st.tabs([
    "🌸 꽃잎으로 예측하기",
    "🔍 원하는 속성 2개로 예측하기"
])


# 탭 1: 기존 꽃잎 길이와 너비
with tab1:

    st.header("꽃잎 길이와 너비로 품종 예측")

    st.write(
        "꽃잎 길이와 꽃잎 너비를 입력하여 "
        "붓꽃의 품종을 예측합니다."
    )

    prediction_page([
        "꽃잎 길이",
        "꽃잎 너비"
    ])


# 탭 2: 사용자가 원하는 속성 2개 선택
with tab2:

    st.header("원하는 속성 2개 선택하기")

    st.write(
        "네 가지 특징 중 원하는 두 가지를 선택해 보세요."
    )

    col1, col2 = st.columns(2)

    with col1:
        feature1 = st.selectbox(
            "첫 번째 속성 선택",
            features,
            index=0,
            key="feature1"
        )

    available_features = [
        feature for feature in features
        if feature != feature1
    ]

    default_index = (
        available_features.index("꽃받침 너비")
        if "꽃받침 너비" in available_features
        else 0
    )

    with col2:
        feature2 = st.selectbox(
            "두 번째 속성 선택",
            available_features,
            index=default_index,
            key="feature2"
        )

    st.info(
        f"선택한 속성: {feature1} + {feature2}"
    )

    prediction_page([
        feature1,
        feature2
    ])


# 하단 정보
st.divider()

st.caption(
    "Iris 데이터 150개를 이용한 붓꽃 품종 분류 프로그램"
)

st.caption(
    "사용 알고리즘: SVM, KNN, Random Forest"
)
