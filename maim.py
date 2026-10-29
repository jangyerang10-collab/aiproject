import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st. text_imput('이름을 압력해주세요')
b=st.selecbox('좋아하는 음식을 선택하세요!',['스테이크','빵','귤']
if st.button('인사말 생성'):
  st.write('반갑습니다!')
