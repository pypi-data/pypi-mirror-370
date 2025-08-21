import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from dython.nominal import associations
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import gaussian_kde


def plot_qq_plot(x, figsize=(8, 6), title="Q-Q Plot (with seaborn)"):
    (osm, osr), (slope, intercept, r) = stats.probplot(x, dist="norm") # osm: theoretical, osr: ordered sample

    # Tính đường thẳng lý thuyết
    line = slope * np.array(osm) + intercept

    # Vẽ bằng seaborn
    sns.set(rc={'axes.facecolor': '#fcf0dc'}, style='darkgrid')
    fig = plt.figure(figsize=figsize)

    # Scatter plot của dữ liệu thực
    sns.scatterplot(x=osm, y=osr, s=60, color='dodgerblue')

    # Vẽ đường lý thuyết
    sns.lineplot(x=osm, y=line, color="red", linestyle="--", label="Theoretical Line")

    plt.xlabel("Theoretical Quantiles")
    plt.ylabel("Sample Quantiles")
    plt.title(title, fontsize=18)
    plt.grid(True)
    plt.legend()
    return fig



def corr_matrix(data):
    a = associations(
    data,
    nominal_columns='auto',
    plot=False,
    title="Correlation Matrix (Mixed Types)",
    figsize=(20, 20)
)
    return a

def plot_corr_matrix(data, figsize=(12, 10), title='Correlation Matrix'):
    a = corr_matrix(data)
# Reset background style
    sns.set_style('whitegrid')

    # Calculate the correlation matrix excluding the 'CustomerID' column
    corr = a['corr']

    # Define a custom colormap
    colors = ['#ff6200', '#ffcaa8', 'white', '#ffcaa8', '#ff6200']
    my_cmap = LinearSegmentedColormap.from_list('custom_map', colors, N=256)

    # Create a mask to only show the lower triangle of the matrix (since it's mirrored around its 
    # top-left to bottom-right diagonal)
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask, k=1)] = True

    # Plot the heatmap
    fig = plt.figure(figsize=figsize)
    sns.heatmap(corr, mask=mask, cmap=my_cmap, annot=True, center=0, fmt='.2f', linewidths=2)
    plt.title(title, fontsize=14)
    return a['corr'], fig


def plot_count_null(data: pd.DataFrame, figsize=(12, 10), color='#ff6200', title='Count Null'):
    num_null_col = data.isnull().sum(axis=1)
    c = num_null_col.value_counts().reset_index()
    c.columns = ['num_null', 'count']
    c.sort_values(by='num_null', ascending=True, inplace=True)
    sns.set_style('whitegrid')
    fig = plt.figure(figsize=figsize)
    sns.barplot(y='num_null',x='count',data=c, color=color)
    plt.title(title, fontsize=14)
    return c, fig


def plot_categorical_feature(value, figsize=(7,3), color='#ff6200', title='Categorical Feature'):
    sns.set_theme(rc={'axes.facecolor': '#fcf0dc'}, style='darkgrid')
    if not isinstance(value, pd.Series):
        value = pd.Series(value)
    c1 = value.value_counts(dropna=False).reset_index()
    c1.columns = ['value', 'count']
    c2 = value.value_counts(dropna=False, normalize=True).reset_index()
    c2.columns = ['value', 'percentage']
    c = c1.merge(c2, on='value', how='left')
    c.columns = ['value', 'count', 'percentage']
    c['value'] = c['value'].fillna('NaN')
    fig = plt.figure(figsize=figsize)
    sns.barplot(y='value', x='count', data=c, color=color)
    plt.ylabel('')
    for i, (v1,v2) in enumerate(zip(c['count'], c['percentage'])):
        plt.text(v1, i, f"{v1} ({v2:.2%})", va='center')
    plt.title(title, fontsize=14)
    return fig

def plot_categorical_features(data, cat_cols, figsize=(10, 5), color='#ff6200'):
    figs = []
    for col in cat_cols:
        value = data[col].values 
        fig = plot_categorical_feature(value, figsize=figsize, color=color, title=col)
        figs.append(fig)
    return figs

def plot_numerical_feature(value, figsize=(10,5), color='#ff6200', title='Numerical Feature'):
    sns.set_theme(rc={'axes.facecolor': '#fcf0dc'}, style='darkgrid')

    fig, ax = plt.subplots(figsize=figsize, ncols=2)
    _ = sns.kdeplot(value, ax=ax[0], color=color)
    ax[0].set_title('Density Plot')
    _ = sns.ecdfplot(value, ax=ax[1], color=color)
    ax[1].set_title('ECDF Plot')
    plt.title(title, fontsize=14)
    return fig

def plot_numerical_features(data, num_cols, figsize=(10, 5), color='#ff6200'):
    figs = []
    for col in num_cols:
        value = data[col].values 
        fig = plot_numerical_feature(value, figsize=figsize, color=color, title=col)
        figs.append(fig)
    return figs


def plot_distribution_cluster(data, col, 
                              bins, bin_labels, 
                              cluster_column='cluster_kmean', 
                              colors=None, 
                              cluster_labels=None, 
                              cut_point=None, 
                              cut_label=None, 
                              y_min=None, 
                              y_max=None):
    fig = plt.figure(figsize=(15, 6))
    clusters = sorted(data[cluster_column].unique())
    for cluster in clusters:
        cluster_data = data[data[cluster_column] == cluster][col]
        label = cluster_labels[cluster] if cluster_labels else f'Nhóm {cluster}'
        binned = pd.cut(cluster_data, bins=bins, labels=bin_labels, include_lowest=True, right=False)
        percent_dist = binned.value_counts(normalize=True).sort_index() * 100
        color = colors[cluster] if colors else None
        sns.barplot(percent_dist, color=color, label=label, alpha=0.3)
    if cut_point is not None:
        plt.vlines(x=cut_point, ymin=y_min, ymax=y_max, color='black', linestyles='--', label=cut_label)
    plt.ylabel('Tỷ lệ (%)')
    plt.legend(loc='upper right')
    plt.title(f'Phân phối của {col} trong {len(clusters)} Nhóm')
    return fig

def plot_kde_cluster(data, col, 
                     cluster_column='cluster_kmean', 
                     colors=None,
                     cluster_labels=None, 
                     cut_point=None, 
                     cut_label=None, 
                     y_min=None, 
                     y_max=None):
    """
    Vẽ đường mật độ xác suất (KDE) cho các nhóm cluster
    
    Parameters:
    -----------
    data : DataFrame
        Dữ liệu đầu vào
    col : str
        Tên cột cần vẽ
    cluster_column : str
        Tên cột chứa nhãn cluster
    colors : list
        Danh sách màu cho các nhóm
    cluster_labels : list
        Danh sách nhãn cho các nhóm
    cut_point : float
        Điểm cắt để vẽ đường thẳng
    cut_label : str
        Nhãn cho điểm cắt
    y_min : float
        Giá trị y tối thiểu cho đường cắt
    y_max : float
        Giá trị y tối đa cho đường cắt
    """
    plt.figure(figsize=(10, 6))
    
    # Lấy các nhóm unique
    clusters = sorted(data[cluster_column].unique())
    
    # Vẽ KDE cho từng nhóm
    for i, cluster in enumerate(clusters):
        cluster_data = data[data[cluster_column] == cluster][col]
        label = cluster_labels[i] if cluster_labels else f'Nhóm {cluster}'
        color = colors[i] if colors else None
        sns.kdeplot(cluster_data, color=color, label=label, linewidth=2)
    
    # Vẽ đường cắt nếu có
    if cut_point is not None:
        plt.vlines(x=cut_point, ymin=y_min, ymax=y_max, color='black', linestyles='--', 
                  label=cut_label if cut_label else f'Điểm cắt = {cut_point}')
    
    plt.title(f"Đường mật độ xác suất cho {len(clusters)} Nhóm \n với {col}")
    plt.xlabel("Giá trị")
    plt.ylabel("Mật độ")
    plt.legend()
    plt.grid(True)
    plt.show()
# Tính phần trăm



def find_threshold(data, col, cluster_column='cluster_kmean', right_clusters=[3]):
    """
    Tìm điểm cắt tối ưu giữa hai nhóm dựa trên giao điểm của KDE
    
    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame chứa dữ liệu
    col : str
        Tên cột cần tìm điểm cắt
    cluster_column : str
        Tên cột chứa nhãn cluster
    right_cluster : int
        Nhãn của nhóm bên phải (mặc định là 3)
    
    Returns:
    --------
    float
        Điểm cắt tối ưu
    """
    data_class_right = data[data[cluster_column].isin(right_clusters)][col].values
    data_class_left = data[~data[cluster_column].isin(right_clusters)][col].values

    # KDE
    kde_right = gaussian_kde(data_class_right)
    kde_left = gaussian_kde(data_class_left)

    # Trục x
    x_vals = np.linspace(min(data[col]), max(data[col]), 1000)
    
    # Mật độ
    pdf_right = kde_right(x_vals)
    pdf_left = kde_left(x_vals)
    
    def find_intersection(x, y1, y2):
        idx = np.argmin(np.abs(y1 - y2))
        return x[idx]

    threshold = find_intersection(x_vals, pdf_right, pdf_left)
    return threshold