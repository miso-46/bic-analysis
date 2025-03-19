import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
    if data is None:
        data = transform_data()
    # 数値データだけ抽出（文字列型などは相関計算の対象外となるため）
    df_numeric = data.select_dtypes(include=[np.number])
    corr = df_numeric.corr()
    fig, ax = plt.subplots(figsize=(20, 15))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Correlation Heatmap")
    plt.tight_layout()
    return fig

# 多重共線性
def get_vif(data: pd.DataFrame) -> pd.DataFrame:
    vif_df = pd.DataFrame()
    vif_df["feature"] = data.columns
    vif_df["VIF"] = [variance_inflation_factor(data.values, i) for i in range(data.shape[1])]
    return vif_df


