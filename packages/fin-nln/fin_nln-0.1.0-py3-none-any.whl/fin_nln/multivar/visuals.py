# multivariate_visualizations.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import mutual_info_regression

import dcor
import statsmodels.api as sm
from statsmodels.tsa.stattools import ccf

# Optional imports (commented out unless used)
# from arch import arch_model
# import umap

# ---------------------------------------------
# Correlation Heatmap
# ---------------------------------------------
def plot_correlation_heatmap(data: pd.DataFrame, method: str = 'pearson'):
    corr = data.corr(method=method)
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(f'{method.capitalize()} Correlation Heatmap')
    plt.show()

# ---------------------------------------------
# Pairwise Scatter Plot
# ---------------------------------------------
def plot_pairwise_scatter(data: pd.DataFrame, hue: str = None):
    sns.pairplot(data, hue=hue)
    plt.suptitle('Pairwise Scatter Plot', y=1.02)
    plt.show()

# ---------------------------------------------
# Rolling Correlation
# ---------------------------------------------
def plot_rolling_correlation(x: pd.Series, y: pd.Series, window: int = 30):
    rolling_corr = x.rolling(window).corr(y)
    plt.plot(rolling_corr)
    plt.title(f'Rolling Correlation ({window}-period)')
    plt.xlabel('Time')
    plt.ylabel('Correlation')
    plt.grid(True)
    plt.show()

# ---------------------------------------------
# Cross Correlation Function Plot
# ---------------------------------------------
def plot_ccf(x: pd.Series, y: pd.Series, lags: int = 40):
    ccf_vals = ccf(x, y)[:lags]
    plt.stem(range(lags), ccf_vals, use_line_collection=True)
    plt.title('Cross-Correlation Function')
    plt.xlabel('Lag')
    plt.ylabel('Correlation')
    plt.grid(True)
    plt.show()

# ---------------------------------------------
# Distance Correlation Bar Plot
# ---------------------------------------------
def plot_distance_correlation(data: pd.DataFrame, target_col: str):
    target = data[target_col].values
    dcor_vals = {
        col: dcor.distance_correlation(data[col].values, target)
        for col in data.columns if col != target_col
    }
    sorted_dcor = dict(sorted(dcor_vals.items(), key=lambda item: item[1], reverse=True))
    plt.bar(sorted_dcor.keys(), sorted_dcor.values())
    plt.xticks(rotation=45)
    plt.title('Distance Correlation with Target')
    plt.tight_layout()
    plt.show()

# ---------------------------------------------
# Mutual Information Score Plot
# ---------------------------------------------
def plot_mutual_information(data: pd.DataFrame, target_col: str):
    X = data.drop(columns=[target_col])
    y = data[target_col]
    mi = mutual_info_regression(X, y)
    mi_series = pd.Series(mi, index=X.columns).sort_values(ascending=False)
    mi_series.plot(kind='bar', title='Mutual Information Scores')
    plt.ylabel('Score')
    plt.tight_layout()
    plt.show()

# ---------------------------------------------
# PCA Projection
# ---------------------------------------------
def plot_pca_projection(data: pd.DataFrame, n_components: int = 2):
    X_scaled = StandardScaler().fit_transform(data)
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(X_scaled)
    plt.scatter(components[:, 0], components[:, 1], alpha=0.7)
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.title('PCA Projection')
    plt.grid(True)
    plt.show()

# ---------------------------------------------
# t-SNE Projection
# ---------------------------------------------
def plot_tsne_projection(data: pd.DataFrame, perplexity: int = 30):
    X_scaled = StandardScaler().fit_transform(data)
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    tsne_result = tsne.fit_transform(X_scaled)
    plt.scatter(tsne_result[:, 0], tsne_result[:, 1], alpha=0.7)
    plt.title('t-SNE Projection')
    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.grid(True)
    plt.show()

# ---------------------------------------------
# Testing Section
# ---------------------------------------------
if __name__ == "__main__":
    # Generate synthetic data for testing
    np.random.seed(0)
    df = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100) * 2 + 1,
        'C': np.sin(np.linspace(0, 10, 100)),
        'D': np.random.randint(0, 100, 100)
    })
    df['Target'] = df['A'] * 0.5 + df['B'] * 0.3 + np.random.normal(0, 1, 100)

    # Run visualizations
    plot_correlation_heatmap(df)
    plot_pairwise_scatter(df)
    plot_rolling_correlation(df['A'], df['B'])
    plot_ccf(df['A'], df['B'])
    plot_distance_correlation(df, 'Target')
    plot_mutual_information(df, 'Target')
    plot_pca_projection(df.drop(columns='Target'))
    plot_tsne_projection(df.drop(columns='Target'))
