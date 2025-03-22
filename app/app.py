import streamlit as st
import numpy as np
from data_access import get_data
from options import get_store_options, get_category_options
from data_merge import merge_data
from data_modify import transform_data
from ml_model import get_correlation_heatmap, get_vif, get_tsne_plot, meanshift_clustering, evaluate_random_forest_classifier

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
                st.session_state.heatmap_fig = get_correlation_heatmap(df_encoded)
        except Exception as e:
            st.error(f"相関ヒートマップの描画中にエラーが発生しました: {e}")
    if "heatmap_fig" in st.session_state:
         st.pyplot(st.session_state.heatmap_fig)
    

    # 多重共線性（VIF）の測定ボタン
    if st.button("多重共線性（VIF）を測定"):
        try:
            df_numeric = df_encoded.select_dtypes(include=[np.number]).dropna().astype(float)
            if df_numeric.empty:
                st.error("数値カラムが存在しないか、欠損値のみのためVIFを計算できません。")
            else:
                st.session_state.vif_df = get_vif(df_numeric)
        except Exception as e:
            st.error(f"多重共線性（VIF）計算中にエラーが発生しました: {e}")
    if "vif_df" in st.session_state:
         st.write("多重共線性（VIF）計算結果:")
         st.dataframe(st.session_state.vif_df)

    # t-SNE の散布図を描画するボタン
    if st.button("t-SNE の散布図を描画"):
        try:
            st.session_state.tsne_fig = get_tsne_plot(df_encoded)
        except Exception as e:
            st.error(f"t-SNE の散布図を描画中にエラーが発生しました: {e}")
    if "tsne_fig" in st.session_state:
         st.pyplot(st.session_state.tsne_fig)

    # MeanShift（教師なし学習）によるクラスタリングを実施し、t-SNEの散布図にクラスタごとに色分け
    # 並行座標プロットを表示する
    if st.button("MeanShiftクラスタリングを実行"):
        try:
            tsne_ms_fig, parallel_fig, n_clusters_ms, df_cluster = meanshift_clustering(df_encoded)
            st.session_state.tsne_ms_fig = tsne_ms_fig
            st.session_state.parallel_fig = parallel_fig
            st.session_state.n_clusters_ms = n_clusters_ms
            st.session_state.df_for_cluster = df_cluster
        except Exception as e:
            st.error(f"MeanShiftクラスタリング中にエラーが発生しました: {e}")
    if ("tsne_ms_fig" in st.session_state and 
        "n_clusters_ms" in st.session_state and
        "parallel_fig" in st.session_state):
         st.write(f"MeanShiftの推定クラスタ数: {st.session_state.n_clusters_ms}")
         st.pyplot(st.session_state.tsne_ms_fig)
         st.pyplot(st.session_state.parallel_fig)

    # MeanShiftのクラスタレベルを疑似的な「目的変数」として分類モデルを作成、疑似的どの特徴量がクラスタ分割に寄与しているか」を可視化
    st.write("モデルの作成はMeanShiftクラスタリングの実行後にクリックしてください")
    if  st.button("モデルの作成（ランダムフォレスト）"):
        try:
            if "df_for_cluster" not in st.session_state:
                st.error("MeanShiftクラスタリングが実行されていません。")
            else:
                # MeanShiftクラスタリングで作成した df_for_cluster を利用
                df_cluster = st.session_state.df_for_cluster

                # クラスタラベル以外の列を特徴量として使用（不要なクラスタ列が存在する場合は除外）
                X = df_cluster.drop(columns=["cluster_ms"], errors="ignore").copy()
                y = df_cluster["cluster_ms"].astype(str)
                
                fig_cm, class_rep, feature_importances = evaluate_random_forest_classifier(X, y)
                st.pyplot(fig_cm)
                st.text(class_rep)
                st.dataframe(feature_importances)
        except Exception as e:
            st.error(f"ランダムフォレスト評価中にエラーが発生しました: {e}")
    
