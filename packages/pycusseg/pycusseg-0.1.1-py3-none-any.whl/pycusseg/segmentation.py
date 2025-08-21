import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from yellowbrick.cluster import SilhouetteVisualizer
from kmodes.kmodes import KModes
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def get_score_kmean(data: pd.DataFrame, start_k: int=2, stop_k: int=10) -> tuple[list[float], list[float]]:
    """
    Calculate Silhouette scores and inertia values for KMeans clustering over a range of cluster numbers.

    Parameters:
        data (pd.DataFrame): Input data for clustering.
        start_k (int): The starting number of clusters (inclusive).
        stop_k (int): The ending number of clusters (inclusive).

    Returns:
        tuple[list[float], list[float]]:
            - silhouette_scores: List of Silhouette scores for each k.
            - inertias: List of inertia values for each k.
    """
    silhouette_scores = []
    inertias = []
    # Iterate through the range of k values
    for k in range(start_k, stop_k + 1):
        clus = KMeans(n_clusters=k, init='k-means++', n_init=10, max_iter=100, random_state=0)
        clus.fit(data)
        labels = clus.predict(data)
        score = silhouette_score(data, labels)
        inertias.append(clus.inertia_)
        silhouette_scores.append(score)
    return silhouette_scores, inertias

def get_score_kmodes(data: pd.DataFrame, start_k: int=2, stop_k: int=10) -> tuple[list[float], list[float]]:
    """
    Calculate Silhouette scores and cost values for KModes clustering over a range of cluster numbers.

    Parameters:
        data (pd.DataFrame): Input categorical data for clustering.
        start_k (int): The starting number of clusters (inclusive).
        stop_k (int): The ending number of clusters (inclusive).

    Returns:
        tuple[list[float], list[float]]:
            - silhouette_scores: List of Silhouette scores for each k (using Hamming distance on label-encoded data).
            - costs: List of cost values (sum of dissimilarities) for each k.
    """
    X_encoded = data.apply(LabelEncoder().fit_transform)
    silhouette_scores = []
    costs = []
    for k in range(start_k, stop_k + 1):
        clus = KModes(n_clusters=k, init='Cao', n_init=5, verbose=0, random_state=42)
        labels = clus.fit_predict(data) 
        score = silhouette_score(X_encoded, labels, metric='hamming')
        costs.append(clus.cost_)
        silhouette_scores.append(score)
    return silhouette_scores, costs

def plot_elbow_method(values: list[float], start_k: int, stop_k: int, title: str="Elbow Method", ylabel: str="Inertia") -> plt.Figure:
    """
    Plot the Elbow Method graph for clustering evaluation.

    Parameters:
        values (list[float]): List of metric values (e.g., inertia or cost) for each k.
        start_k (int): The starting number of clusters (inclusive).
        stop_k (int): The ending number of clusters (inclusive).
        title (str, optional): Title of the plot. Default is "Elbow Method".
        ylabel (str, optional): Label for the y-axis. Default is "Inertia".

    Returns:
        matplotlib.figure.Figure: The matplotlib Figure object containing the plot.
    """
    sns.set_theme(style='darkgrid', rc={'axes.facecolor': '#fcf0dc'})
    sns.set_palette(['darkorange'])
    fig = plt.figure(figsize=(20, 5))
    plt.plot(range(start_k, stop_k + 1), values, marker='o')
    plt.title(title)
    plt.xlabel("Số cụm (k)")
    plt.xticks(range(start_k, stop_k + 1))
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.show()
    return fig

def plot_silhouette_score(silhouette_scores: list[float], start_k: int, stop_k: int) -> plt.Figure:
    """
    Plot the Silhouette Score for a range of cluster numbers.

    Parameters:
        silhouette_scores (list[float]): List of Silhouette scores for each k.
        start_k (int): The starting number of clusters (inclusive).
        stop_k (int): The ending number of clusters (inclusive).

    Returns:
        matplotlib.figure.Figure: The matplotlib Figure object containing the plot.
    """
    sns.set_theme(style='darkgrid', rc={'axes.facecolor': '#fcf0dc'})
    sns.set_palette(['darkorange'])
    fig = plt.figure(figsize=(20, 5))
    plt.plot(range(start_k, stop_k + 1), silhouette_scores, marker='o')
    plt.title("Silhouette Score")
    plt.xlabel("Number of clusters (k)")
    plt.xticks(range(start_k, stop_k + 1))
    plt.ylabel("Silhouette Score")
    plt.grid(True)
    plt.show()
    return fig


def silhouette_analysis(df: pd.DataFrame, start_k: int, stop_k: int, figsize: tuple[int, int]=(15, 16)) -> plt.Figure:
    """
    Perform Silhouette analysis for a range of k values and visualize the results.

    Parameters:
        df (pd.DataFrame): The input data for clustering.
        start_k (int): The starting number of clusters (inclusive).
        stop_k (int): The ending number of clusters (inclusive).
        figsize (tuple[int, int], optional): The size of the matplotlib figure. Default is (15, 16).

    Returns:
        matplotlib.figure.Figure: The matplotlib Figure object containing the Silhouette analysis plots.

    This function generates two types of plots:
        1. A line plot showing the average Silhouette score for each k in the specified range.
        2. Individual Silhouette plots for each k value, visualizing the distribution of Silhouette scores for each cluster.
    """
    # Set the size of the figure
    plt.figure(figsize=figsize)

    # Create a grid with (stop_k - start_k + 1) rows and 2 columns
    grid = gridspec.GridSpec(stop_k - start_k + 1, 2)

    # First plot: Silhouette scores for different k values
    sns.set_palette(['darkorange'])

    silhouette_scores = []

    # Iterate through the range of k values
    for k in range(start_k, stop_k + 1):
        km = KMeans(n_clusters=k, init='k-means++', n_init=10, max_iter=100, random_state=0)
        km.fit(df)
        labels = km.predict(df)
        score = silhouette_score(df, labels)
        silhouette_scores.append(score)

    best_k = start_k + silhouette_scores.index(max(silhouette_scores))

    plt.plot(range(start_k, stop_k + 1), silhouette_scores, marker='o')
    plt.xticks(range(start_k, stop_k + 1))
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Silhouette score')
    plt.title('Average Silhouette Score for Different k Values', fontsize=15)

    # Add the optimal k value text to the plot
    optimal_k_text = f'The k value with the highest Silhouette score is: {best_k}'
    plt.text(10, 0.23, optimal_k_text, fontsize=12, verticalalignment='bottom', 
             horizontalalignment='left', bbox=dict(facecolor='#fcc36d', edgecolor='#ff6200', boxstyle='round, pad=0.5'))
             

    # Second plot (subplot): Silhouette plots for each k value
    colors = sns.color_palette("bright")

    for i in range(start_k, stop_k + 1):    
        km = KMeans(n_clusters=i, init='k-means++', n_init=10, max_iter=100, random_state=0)
        row_idx, col_idx = divmod(i - start_k, 2)

        # Assign the plots to the second, third, and fourth rows
        ax = plt.subplot(grid[row_idx + 1, col_idx])

        visualizer = SilhouetteVisualizer(km, colors=colors, ax=ax)
        visualizer.fit(df)

        # Add the Silhouette score text to the plot
        score = silhouette_score(df, km.labels_)
        ax.text(0.97, 0.02, f'Silhouette Score: {score:.2f}', fontsize=12, \
                ha='right', transform=ax.transAxes, color='red')

        ax.set_title(f'Silhouette Plot for {i} Clusters', fontsize=15)

    plt.tight_layout()
    plt.show()