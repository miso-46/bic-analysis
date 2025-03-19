import streamlit as st
from data_access import get_data
from options import get_store_options, get_category_options
from ml_model import get_correlation_heatmap
from data_merge import merge_data
from data_modify import transform_data

st.title("接客データ分析アプリ")

# 店舗選択
store_options = get_store_options()
store = st.sidebar.selectbox("店舗を選択", store_options)

# カテゴリ選択
category_options = get_category_options()
category = st.sidebar.selectbox("家電カテゴリを選択", category_options)

# 分析実行ボタン
if st.sidebar.button("分析を実行"):
    st.sidebar.write("選択された店舗:", store)
    st.sidebar.write("選択された家電カテゴリ:", category)

# タブを用意
tabs = st.tabs(["判断軸分析", "店員呼び出し分析", "DB接続確認", "機械学習"])


# タブ1: 判断軸分析
with tabs[0]:
    st.write("ここに判断軸分析のコンテンツを追加します。")

# タブ2: 店員呼び出し分析
with tabs[1]:
    st.write("ここに店員呼び出し分析のコンテンツを追加します。")

# タブ3: DB接続確認
with tabs[2]:
    st.header("DB確認")
    # デバッグ用に選択された値を表示
    st.write("DEBUG: 選択された店舗(store_id):", store)
    st.write("DEBUG: 選択されたカテゴリ(category_id):", category)

    try:
        df = get_data(store, category)
        print("取得したデータフレーム:", df)
        if df is None:
            st.error("データ取得関数がNoneを返しました。")
        elif df.empty:
            st.write("DBのデータがありません。")
        else:
            st.success("データ取得に成功しました。")
            st.write("DBから取得したデータ（最初の5行）:")
            st.dataframe(df.head(5))
    except Exception as e:
        st.error(f"データ取得中にエラーが発生しました: {e}")
        st.error(f"エラー詳細: {e}")

# タブ4:機械学習
with tabs[3]:
    st.header("機械学習")
    
    st.write("データのマージ結果")
    df_merged = merge_data()
    st.dataframe(df_merged.head())

    st.write("データのエンコーディング結果")
    df_encoded = transform_data()
    st.dataframe(df_encoded.head())


    if st.button("相関ヒートマップの描画を実行"):
        try:
            df_encoded = transform_data()
            st.write("取得したデータ（先頭5行）:", df_encoded.head())
            if df_encoded is None or df_encoded.empty:
                st.error("機械学習用のデータがありません。")
            else:
                heatmap_fig = get_correlation_heatmap(df_encoded)
                st.pyplot(heatmap_fig)
        except Exception as e:
            st.error(f"相関ヒートマップの描画中にエラーが発生しました: {e}")
    
