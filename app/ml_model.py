# ml_model.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
from sklearn.mixture import BayesianGaussianMixture
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from pandas.plotting import parallel_coordinates
from statsmodels.stats.outliers_influence import variance_inflation_factor

from data_modify import transform_data  # 変形済みのDataFrameを取得

# 相関ヒートマップの描画
def get_correlation_heatmap(data: pd.DataFrame = None) -> plt.Figure:
    df_numeric = data.select_dtypes(include=[np.number])
    corr = df_numeric.corr()
    fig, ax = plt.subplots(figsize=(20, 15))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Correlation Heatmap")
    return fig

# 多重共線性
def get_vif(data: pd.DataFrame) -> pd.DataFrame:
    X = data.copy()
    X = X.assign(const=1)  # 定数項を追加
    vif_data = []
    for i in range(X.shape[1]):
        col_name = X.columns[i]
        vif_value = variance_inflation_factor(X.values, i)
        vif_data.append((col_name, vif_value))
    vif_df = pd.DataFrame(vif_data, columns=["Variable", "VIF"]).sort_values("VIF", ascending=False)
    return vif_df

# t-SNE の散布図を描画
def get_tsne_plot(data: pd.DataFrame) -> plt.Figure:
    # 数値型のカラムだけを抽出し、欠損値を除去
    df_num = data.select_dtypes(include=['int64', 'float64']).dropna()
    # TSNE による2次元変換
    tsne_result = TSNE(n_components=2, learning_rate='auto', init='random').fit_transform(df_num)
    # Figure と Axes を作成し散布図を描画
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(tsne_result[:, 0], tsne_result[:, 1])
    ax.set_title("t-SNE")
    return fig

# MeanShift（教師なし学習）の関数
def meanshift_clustering(data: pd.DataFrame, quantile: float = 0.2, n_samples: int = 500):
    # 数値型のカラムのみを抽出し、欠損値を含む行は除外
    df_numeric = data.select_dtypes(include=['int64','float64']).dropna()
    # 必要に応じて reception_id を除外
    df_for_cluster = df_numeric.drop(columns=['reception_id'], errors='ignore')

    # バンド幅を推定
    bandwidth = estimate_bandwidth(df_for_cluster, quantile=quantile, n_samples=n_samples)
    # MeanShift でクラスタリング
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(df_for_cluster)

    labels_ms = ms.labels_
    n_clusters_ms = len(np.unique(labels_ms))

    # カラーパレット（viridis）を生成
    cmap = cm.get_cmap('viridis', n_clusters_ms)
    palette = [cmap(i) for i in range(n_clusters_ms)]

    # t-SNEで2次元に次元削減し散布図を描画（クラスタごとに色分け）
    tsne = TSNE(n_components=2, learning_rate='auto', init='random')
    tsne_result = tsne.fit_transform(df_for_cluster)
    fig_tsne, ax_tsne = plt.subplots(figsize=(10, 8))
    scatter = ax_tsne.scatter(tsne_result[:, 0], tsne_result[:, 1], c=labels_ms, cmap='viridis')
    ax_tsne.set_title(f"t-SNE with MeanShift Clusters (n_clusters={n_clusters_ms})")
    cbar = fig_tsne.colorbar(scatter, ax=ax_tsne)
    cbar.set_label("Cluster Label")

    # --- 並行座標プロット ---
    # クラスタラベルを文字列として新たなカラムに追加し、順序を固定
    df_for_cluster["cluster_ms"] = labels_ms.astype(str)
    df_for_cluster["cluster_ms"] = pd.Categorical(
        df_for_cluster["cluster_ms"],
        categories=[str(i) for i in range(n_clusters_ms)],
        ordered=True
    )
    fig_parallel, ax_parallel = plt.subplots(figsize=(12, 6))
    parallel_coordinates(
        df_for_cluster.reset_index(drop=True),
        class_column="cluster_ms",
        color=palette,
        sort_labels=False,
        ax=ax_parallel
    )
    ax_parallel.set_xticklabels(ax_parallel.get_xticklabels(), rotation=45, ha='right')
    ax_parallel.set_title(f"Parallel Coordinates Plot by MeanShift (n_clusters={n_clusters_ms})")
    
    return fig_tsne, fig_parallel, n_clusters_ms, df_for_cluster # df_for_clusterにはクラスタリングで分類したカラムが結合されている


# ランダムフォレストによってモデルを作成、混同行列、特徴量重要度を返す
def evaluate_random_forest_classifier(X: pd.DataFrame, y, test_size: float = 0.3, random_state: int = 42, n_estimators: int = 100):
    # 学習データとテストデータに分割（stratify によりラベルの分布を保つ）
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # ランダムフォレストで学習
    clf = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    # 混同行列の計算とヒートマップ作成
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
    ax.set_title("Confusion Matrix Heatmap")
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    
    # 分類レポートの取得
    class_rep = classification_report(y_test, y_pred)
    
    # 特徴量重要度の計算
    feature_importances = pd.Series(clf.feature_importances_, index=X.columns).sort_values(ascending=False)
    
    return fig, class_rep, feature_importances

