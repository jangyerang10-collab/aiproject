
# -------------------------
# 1. 데이터 불러오기
# -------------------------

st.sidebar.header("📂 데이터 불러오기")

uploaded_file = st.sidebar.file_uploader(
    "공공데이터 CSV 파일 업로드",
    type=["csv"]
)

@st.cache_data
def load_data(file):
    try:
        return pd.read_csv(file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        if hasattr(file, "seek"):
            file.seek(0)
        return pd.read_csv(file, encoding="cp949")

# GitHub 저장소 최상위 폴더의 CSV 파일 경로
if "__file__" in globals():
    DATA_FILE = Path(__file__).resolve().parent.parent / "food_nutrition.csv"
else:
    DATA_FILE = Path("food_nutrition.csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)

elif DATA_FILE.exists():
    df = load_data(DATA_FILE)

else:
    st.error("GitHub 저장소에 food_nutrition.csv 파일이 없습니다.")
    st.write("CSV 파일을 app.py와 같은 최상위 폴더에 올려 주세요.")
    st.stop()

df.columns = df.columns.astype(str).str.strip()
