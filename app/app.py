import streamlit as st
import numpy as np
from data_access import get_data
from options import get_store_options, get_category_options
from data_merge import merge_data
from data_modify import transform_data
from ml_model import get_correlation_heatmap, get_vif, get_tsne_plot, meanshift_clustering, evaluate_random_forest_classifier,get_age_analysis_plots
from chatgpt import interpret_corr_matrix

st.title("接客データ分析アプリ")

# 店舗選択
store_options = get_store_options()
store = st.sidebar.selectbox("店舗を選択", store_options)

# カテゴリ選択
category_options = get_category_options()
category = st.sidebar.selectbox("家電カテゴリを選択", category_options)

# # 分析実行ボタン
# if st.sidebar.button("分析を実行"):
#     st.sidebar.write("選択された店舗:", store)
#     st.sidebar.write("選択された家電カテゴリ:", category)

# タブを用意
tabs = st.tabs(["判断軸分析", "店員呼び出し分析", "DB接続確認", "機械学習"])


# タブ1: 判断軸分析
with tabs[0]:
    st.write("サイドバーで選択した店舗と商品について分析します")
    if st.button("判断軸分析の実行"):
        with st.spinner("分析の実行中"):
            # 変換済みデータを取得(idをドロップしていないデータ)DataFrame ではなくタプルを返している
            # 返り値を2つの変数にアンパックしていないと、df_encoded がタプルになる
            df_encoded, df_encoded_with_id = transform_data()
            
            # フィルタリング：店舗と商品カテゴリに合致するデータのみを抽出
            filtered_df = df_encoded_with_id[
                (df_encoded_with_id["store_id"] == store) & 
                (df_encoded_with_id["reception_category_id"] == category)
            ]

            # 正しくフィルタリングができているかを確認
            st.dataframe(filtered_df.head()) 

            # id類（user_id、category_id、reception_id）はリーケージの原因となりえるため、すべて削除する
            df_encoded_filtered = filtered_df.drop(
                columns=["user_id", "reception_category_id", "reception_id"], 
                errors="ignore"
            )
   
            # クラスタリング実行中
            with st.spinner("クラスタリング実行中"):
                tsne_ms_fig, parallel_fig, n_clusters_ms, df_cluster = meanshift_clustering(df_encoded_filtered)
            
            # クラスタラベルを「Cluster_～」に変換
            df_cluster["cluster_ms"] = df_cluster["cluster_ms"].astype(str)
            df_cluster["cluster_ms"] = "Cluster_" + df_cluster["cluster_ms"]

            # モデリング実行中
            with st.spinner("モデリングの実行中"):
                # df_cluster は MeanShift の結果（"cluster_ms" 列付き）
                # 特徴量 X として不要なクラスタ列を除外、目的変数 y は "cluster_ms" を使用
                X = df_cluster.drop(columns=["cluster", "cluster_bgmm", "cluster_ms"], errors="ignore").copy()
                y = df_cluster["cluster_ms"].astype(str)
                fig_cm, class_rep, feature_importances = evaluate_random_forest_classifier(X, y)
                
        st.success("分析が完了しました。")
        st.write(f"MeanShiftの推定クラスタ数: {n_clusters_ms}")
        st.pyplot(tsne_ms_fig)
        st.pyplot(parallel_fig)
        st.pyplot(fig_cm)
        st.text(class_rep)
        st.dataframe(feature_importances)


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
    df_encoded, df_encoded_with_id = transform_data() # タプルで取得
    st.dataframe(df_encoded.head())


    if st.button("相関ヒートマップの描画を実行"):
        try:
            df_encoded, df_encoded_with_id = transform_data()
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
            
            # クラスタラベルに "Cluster_" を付ける
            df_cluster["cluster_ms"] = df_cluster["cluster_ms"].astype(str)
            df_cluster["cluster_ms"] = "Cluster_" + df_cluster["cluster_ms"]
            
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

                # 年齢分析のプロットを取得して表示
                cluster_age_stats, fig_box, grouped, corr_matrix, fig_corr = get_age_analysis_plots(df_cluster)
                st.write("各クラスタの年齢統計:")
                st.dataframe(cluster_age_stats)
                st.pyplot(fig_box)
                st.write("年齢層ごとのアンケート結果と年齢の平均:")
                st.dataframe(grouped)
                st.write("相関行列:")
                st.dataframe(corr_matrix)
                st.pyplot(fig_corr)

                # 相関行列をセッションステートに保持
                st.session_state.corr_matrix = corr_matrix

        except Exception as e:
            st.error(f"ランダムフォレスト評価中にエラーが発生しました: {e}")
    
    # GPTによる相関行列分析の実行ボタン
    st.write("GPTによる分析はモデルの作成実行後にクリックしてください")
    if st.button("GPTによる相関行列分析を実行"):
        try:
            if "corr_matrix" not in st.session_state:
                st.error("相関行列が見つかりません。先にモデル作成を実行してください。")
            else:
                interpretation = interpret_corr_matrix(st.session_state.corr_matrix)
                st.write("ChatGPT の解釈:")
                st.write(interpretation)
        except Exception as e:
            st.error(f"GPTによる分析中にエラーが発生しました: {e}")
