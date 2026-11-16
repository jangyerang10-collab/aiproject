
# 세 가지 알고리즘의 예측 결과
st.subheader("2. 알고리즘별 품종 예측 결과")

results = {}

for name, model in models.items():
    results[name] = model.predict(input_data)[0]

# 알고리즘별 결과 비교표
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

# 품종별 예측 횟수
vote_counts = pd.Series(results).value_counts()

max_votes = vote_counts.max()
winners = vote_counts[vote_counts == max_votes].index.tolist()

st.write("### 품종별 예측 결과 비교")

vote_df = pd.DataFrame({
    "품종": vote_counts.index,
    "예측 횟수": vote_counts.values
})

st.bar_chart(
    vote_df.set_index("품종")
)

# 최종 비교 결과
if len(winners) == 1:
    st.success(
        f"가장 많은 알고리즘이 예측한 품종: {winners[0]} "
        f"({max_votes}/3)"
    )
else:
    st.warning(
        "예측 결과가 동률입니다: " + ", ".join(winners)
    )

# 알고리즘별 예측 일치 여부
if len(winners) == 1 and max_votes == 3:
    st.success("세 가지 알고리즘의 예측 결과가 모두 일치합니다!")
elif max_votes == 2:
    st.info("세 가지 알고리즘 중 두 가지의 예측 결과가 일치합니다.")
else:
    st.warning("세 가지 알고리즘의 예측 결과가 서로 다릅니다.")
