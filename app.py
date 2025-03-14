import pandas as pd
import streamlit as st

st.title("接客データ分析アプリ")

st.sidebar.write("サイドバーはこちら")
store = st.sidebar.selectbox("店舗を選択", ["店舗A", "店舗B", "店舗C"])
category = st.sidebar.selectbox("家電カテゴリを選択", ["ロボット掃除機", "商品X", "商品Y", "商品Z"])
if st.sidebar.button("分析を実行"):
    st.sidebar.write("選択された店舗:", store)
    st.sidebar.write("選択された家電カテゴリ:", category)

tab1, tab2 = st.tabs(["判断軸分析", "店員呼び出し分析"])
if category in ["商品X", "商品Y", "商品Z"]:
    message = f"{category} のデータがありません"
    with tab1:
        st.write(message)
    with tab2:
        st.write(message)
else:
    with tab1:
        st.write("ここに判断軸分析のコンテンツを追加します。")
    with tab2:
        st.write("ここに店員呼び出し分析のコンテンツを追加します。")
