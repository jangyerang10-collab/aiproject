
from pathlib import Path

@st.cache_data
def load_data():
    # 현재 파이썬 파일의 위치 확인
    current_dir = Path(__file__).resolve().parent

    # CSV가 pages 폴더 또는 상위 폴더에 있는지 확인
    paths = [
        current_dir / "Iris.csv",
        current_dir.parent / "Iris.csv"
    ]

    file_path = next(
        (p for p in paths if p.is_file()),
        None
    )

    if file_path is None:
        st.error("Iris.csv 파일을 찾을 수 없습니다.")
        st.info("GitHub 저장소의 최상위 폴더에 Iris.csv를 업로드해 주세요.")
        st.stop()

    try:
        data = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="utf-8-sig")

    return data

df = load_data()
