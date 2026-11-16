import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC@st.cache_data
def load_data():
    current_dir = Path(__file__).resolve().parent

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
        st.stop()

    try:
        data = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="utf-8-sig")

    return data


df = load_data()
