import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
from db import get_data
from models import SessionLocal, User

load_dotenv()  # .env ファイルの内容を読み込む

st.title("接客データ分析アプリ")

# DBから User テーブルの distinct な store_id を取得して、店舗選択のオプションとする
def get_store_options():
    session = SessionLocal()
    try:
        stores = session.query(User.store_id).distinct().all()
        store_list = sorted([s[0] for s in stores if s[0] is not None])
    finally:
        session.close()
    return store_list

store_options = get_store_options()
store = st.sidebar.selectbox("店舗を選択", store_options)


category = st.sidebar.selectbox("家電カテゴリを選択", ["ロボット掃除機", "商品X", "商品Y", "商品Z"])
if st.sidebar.button("分析を実行"):
    st.sidebar.write("選択された店舗:", store)
    st.sidebar.write("選択された家電カテゴリ:", category)

# 家電カテゴリの選択値を DB の category_id に変換するマッピング（必要に応じて変更）
category_mapping = {"ロボット掃除機": 1, "商品X": 2, "商品Y": 3, "商品Z": 4}

# タブに「判断軸分析」「店員呼び出し分析」「DB確認」を追加
tabs = st.tabs(["判断軸分析", "店員呼び出し分析", "DB確認"])

if category in ["商品X", "商品Y", "商品Z"]:
    message = f"{category} のデータがありません"
    with tabs[0]:
        st.write(message)
    with tabs[1]:
        st.write(message)
else:
    with tabs[0]:
        st.write("ここに判断軸分析のコンテンツを追加します。")
    with tabs[1]:
        st.write("ここに店員呼び出し分析のコンテンツを追加します。")

# DB確認タブで、選択された店舗(store_id)とカテゴリ(category_id)に基づきDBからデータ取得
with tabs[2]:
    st.header("DB確認")
    cat_id = category_mapping.get(category)
    df = get_data(store, cat_id)
    if df.empty:
        st.write("DBのデータがありません。")
    else:
        st.write("DBから取得したデータ（最初の5行）:")
        st.dataframe(df.head(5))

