"""
visuals.py - Essential visualization functions for quantitative time series diagnostics

This module provides a comprehensive set of visualization functions for analyzing 
time series data in quantitative finance applications. Functions include ACF/PACF plots,
time series plots, residual diagnostics, and various nonlinear dynamics visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.nonparametric.kde import KDEUnivariate
from scipy import stats
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import pdist, squareform


def plot(data, title='Time Series Plot', figsize=(12, 6), color='steelblue', 
                     xlabel='Time', ylabel='Value', alpha=0.8, grid=True, ax=None):
    """
    Create a basic time series plot with customizable parameters.
    
    Parameters
    ----------
    data : array-like or pandas Series
        The time series data to plot
    title : str, optional
        Title of the plot
    figsize : tuple, optional
        Figure size as (width, height) in inches
    color : str, optional
        Color of the line plot
    xlabel : str, optional
        Label for the x-axis
    ylabel : str, optional
        Label for the y-axis
    alpha : float, optional
        Transparency of the line (0 to 1)
    grid : bool, optional
        Whether to display grid lines
    ax : matplotlib.axes, optional
        Pre-existing axes to plot on
        
    Returns
    -------
    matplotlib.axes
        The axes containing the plot
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        
    if isinstance(data, pd.Series):
        data.plot(ax=ax, color=color, alpha=alpha)
    else:
        ax.plot(data, color=color, alpha=alpha)
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if grid:
        ax.grid(True, linestyle='--', alpha=0.6)
    
    return ax


def plot_acf_pacf(data, lags=40, figsize=(12, 8), title=None, alpha=0.05):
    """
    Plot ACF and PACF side by side.
    
    Parameters
    ----------
    data : array-like
        Time series data
    lags : int, optional
        Number of lags to include
    figsize : tuple, optional
        Figure size as (width, height) in inches
    title : str, optional
        Title for the combined plot
    alpha : float, optional
        Significance level for confidence intervals
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing the plots
    """
    fig, axes = plt.subplots(2, 1, figsize=figsize)
    
    if title:
        fig.suptitle(title, fontsize=14)
    
    # ACF plot
    plot_acf(data, lags=lags, ax=axes[0], alpha=alpha)
    axes[0].set_title('Autocorrelation Function (ACF)')
    
    # PACF plot
    plot_pacf(data, lags=lags, ax=axes[1], alpha=alpha)
    axes[1].set_title('Partial Autocorrelation Function (PACF)')
    
    plt.tight_layout()
    if title:
        plt.subplots_adjust(top=0.9)
        
    return fig


def plot_residuals_vs_fitted(fitted_values, residuals, figsize=(10, 6), 
                            title='Residuals vs Fitted Values', add_lowess=True):
    """
    Plot residuals against fitted values to check for heteroscedasticity 
    and non-linearity.
    
    Parameters
    ----------
    fitted_values : array-like
        The fitted or predicted values from a model
    residuals : array-like
        The residuals (actual - fitted)
    figsize : tuple, optional
        Figure size as (width, height) in inches
    title : str, optional
        Title for the plot
    add_lowess : bool, optional
        Whether to add a LOWESS smoothed line to help identify patterns
        
    Returns
    -------
    matplotlib.axes
        The axes containing the plot
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Scatter plot
    ax.scatter(fitted_values, residuals, alpha=0.6)
    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='red', linestyle='--')
    
    # Add LOWESS smooth line if requested
    if add_lowess:
        lowess = sm.nonparametric.lowess(residuals, fitted_values, frac=0.3)
        ax.plot(lowess[:, 0], lowess[:, 1], color='orange', 
                linestyle='-', linewidth=2, label='LOWESS')
        ax.legend()
    
    ax.set_title(title)
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('Residuals')
    ax.grid(True, linestyle='--', alpha=0.6)
    
    return ax


def plot_residual_histogram(residuals, bins=30, figsize=(10, 6), kde=True, 
                           title='Histogram of Residuals', normal_fit=True):
    """
    Plot histogram of residuals with optional KDE and normal distribution fit.
    
    Parameters
    ----------
    residuals : array-like
        The residuals to analyze
    bins : int, optional
        Number of histogram bins
    figsize : tuple, optional
        Figure size as (width, height) in inches
    kde : bool, optional
        Whether to overlay a Kernel Density Estimate
    title : str, optional
        Title for the plot
    normal_fit : bool, optional
        Whether to overlay a normal distribution fit
        
    Returns
    -------
    matplotlib.axes
        The axes containing the plot
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate basic statistics
    mean = np.mean(residuals)
    std = np.std(residuals)
    skew = stats.skew(residuals)
    kurtosis = stats.kurtosis(residuals)
    
    # Create histogram with KDE
    sns.histplot(residuals, bins=bins, kde=kde, ax=ax)
    
    # Add normal distribution fit
    if normal_fit:
        x = np.linspace(min(residuals) - 1, max(residuals) + 1, 1000)
        norm_pdf = stats.norm.pdf(x, mean, std)
        ax.plot(x, norm_pdf * len(residuals) * (max(residuals) - min(residuals)) / bins, 
                'r-', linewidth=2, label='Normal Fit')
        ax.legend()
    
    # Add statistics text box
    stats_text = (f'Mean: {mean:.4f}\nStd Dev: {std:.4f}\n'
                 f'Skewness: {skew:.4f}\nKurtosis: {kurtosis:.4f}')
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    ax.set_title(title)
    ax.set_xlabel('Residual Value')
    ax.set_ylabel('Frequency')
    
    return ax


def plot_qq(residuals, figsize=(10, 6), title='Q-Q Plot of Residuals', 
           line='45', alpha=0.7):
    """
    Create a Q-Q plot to check for normality of residuals.
    
    Parameters
    ----------
    residuals : array-like
        The residuals to analyze
    figsize : tuple, optional
        Figure size as (width, height) in inches
    title : str, optional
        Title for the plot
    line : {'45', 's', 'r', 'q', None}, optional
        Reference line to be drawn:
        '45' - 45-degree line
        's' - standardized line
        'r' - robust line
        'q' - line through quartiles
        None - no line
    alpha : float, optional
        Transparency of the points
        
    Returns
    -------
    matplotlib.axes
        The axes containing the plot
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # QQ plot
    qq = sm.qqplot(residuals, line=line, ax=ax, alpha=alpha)
    
    # Calculate Shapiro-Wilk test for normality
    shapiro_test = stats.shapiro(residuals)
    sw_stat, sw_p = shapiro_test
    
    # Add statistics text box
    stats_text = (f'Shapiro-Wilk Test:\nStatistic: {sw_stat:.4f}\n'
                 f'p-value: {sw_p:.4f}')
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    ax.set_title(title)
    
    return ax


def plot_lag_scatter(data, lag=1, figsize=(10, 10), title=None, 
                    alpha=0.6, color='steelblue', add_fit=True):
    """
    Create a lag scatter plot to visually identify nonlinear time dependencies.
    
    Parameters
    ----------
    data : array-like
        Time series data
    lag : int, optional
        Lag to plot against original series
    figsize : tuple, optional
        Figure size as (width, height) in inches
    title : str, optional
        Title for the plot
    alpha : float, optional
        Transparency of the points
    color : str, optional
        Color of the scatter points
    add_fit : bool, optional
        Whether to add linear and nonlinear (LOWESS) fits
        
    Returns
    -------
    matplotlib.axes
        The axes containing the plot
    """
    # Create lagged series
    data_array = np.array(data)
    x = data_array[:-lag]
    y = data_array[lag:]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate correlation
    corr = np.corrcoef(x, y)[0, 1]
    
    # Create scatter plot
    ax.scatter(x, y, alpha=alpha, color=color)
    
    if add_fit:
        # Add linear fit
        coef = np.polyfit(x, y, 1)
        poly1d_fn = np.poly1d(coef) 
        x_sorted = np.sort(x)
        ax.plot(x_sorted, poly1d_fn(x_sorted), 'r-', 
                linewidth=2, label=f'Linear Fit (r = {corr:.3f})')
        
        # Add LOWESS fit
        lowess = sm.nonparametric.lowess(y, x, frac=0.3)
        ax.plot(lowess[:, 0], lowess[:, 1], 'g-', 
                linewidth=2, label='LOWESS Fit')
        
        ax.legend()
    
    if title is None:
        title = f'Lag {lag} Scatter Plot'
    ax.set_title(title)
    ax.set_xlabel(f'$X_t$')
    ax.set_ylabel(f'$X_{{t+{lag}}}$')
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Add correlation to the plot
    ax.text(0.05, 0.95, f'Correlation: {corr:.4f}', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    return ax


def plot_rolling_statistics(data, window=20, figsize=(12, 10), title=None):
    """
    Plot rolling mean and variance to assess stationarity.
    
    Parameters
    ----------
    data : array-like or pandas Series
        Time series data
    window : int, optional
        Rolling window size
    figsize : tuple, optional
        Figure size as (width, height) in inches
    title : str, optional
        Title for the combined plot
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing the plots
    """
    # Convert to pandas Series if not already
    if not isinstance(data, pd.Series):
        if isinstance(data, pd.DataFrame):
            data = data.iloc[:, 0]  # Take first column
        else:
            data = pd.Series(data)
    
    # Calculate rolling statistics
    rolling_mean = data.rolling(window=window).mean()
    rolling_var = data.rolling(window=window).var()
    
    fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
    
    if title:
        fig.suptitle(title, fontsize=14)
    else:
        fig.suptitle(f'Rolling Statistics (Window = {window})', fontsize=14)
    
    # Plot original data
    axes[0].plot(data, color='blue', alpha=0.7, label='Original')
    axes[0].set_title('Original Time Series')
    axes[0].grid(True, linestyle='--', alpha=0.6)
    axes[0].legend()
    
    # Plot rolling mean
    axes[1].plot(rolling_mean, color='red', alpha=0.8, label=f'Rolling Mean ({window})')
    axes[1].set_title(f'Rolling Mean (Window = {window})')
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].legend()
    
    # Plot rolling variance
    axes[2].plot(rolling_var, color='green', alpha=0.8, label=f'Rolling Variance ({window})')
    axes[2].set_title(f'Rolling Variance (Window = {window})')
    axes[2].set_xlabel('Time')
    axes[2].grid(True, linestyle='--', alpha=0.6)
    axes[2].legend()
    
    plt.tight_layout()
    if title:
        plt.subplots_adjust(top=0.9)
    
    return fig


def plot_correlation_heatmap(data, max_lags=10, figsize=(12, 10), 
                            title='Correlation Matrix of Lags', cmap='viridis'):
    """
    Plot correlation matrix heatmap between lagged versions of the time series.
    
    Parameters
    ----------
    data : array-like
        Time series data
    max_lags : int, optional
        Maximum number of lags to include
    figsize : tuple, optional
        Figure size as (width, height) in inches
    title : str, optional
        Title for the plot
    cmap : str, optional
        Colormap for the heatmap
        
    Returns
    -------
    matplotlib.axes
        The axes containing the plot
    """
    # Convert to numpy array if not already
    data_array = np.array(data).flatten()
    
    # Create lagged matrix
    lagged_matrix = np.zeros((len(data_array) - max_lags, max_lags + 1))
    for i in range(max_lags + 1):
        lagged_matrix[:, i] = data_array[max_lags - i:len(data_array) - i]
    
    # Calculate correlation matrix
    corr_matrix = np.corrcoef(lagged_matrix.T)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create heatmap
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap=cmap, 
                xticklabels=range(max_lags + 1), 
                yticklabels=range(max_lags + 1),
                vmin=-1, vmax=1, center=0, cbar_kws={"shrink": .8}, ax=ax)
    
    ax.set_title(title)
    ax.set_xlabel('Lag')
    ax.set_ylabel('Lag')
    
    return ax


def plot_recurrence(data, embed_dim=2, tau=1, threshold=None, figsize=(10, 10), 
                   title='Recurrence Plot', cmap='binary'):
    """
    Create a recurrence plot for identifying deterministic chaos.
    
    Parameters
    ----------
    data : array-like
        Time series data
    embed_dim : int, optional
        Embedding dimension
    tau : int, optional
        Time delay
    threshold : float, optional
        Distance threshold (if None, threshold will be set to 10% of max distance)
    figsize : tuple, optional
        Figure size as (width, height) in inches
    title : str, optional
        Title for the plot
    cmap : str, optional
        Colormap for the plot
        
    Returns
    -------
    matplotlib.axes
        The axes containing the plot
    """
    # Convert to numpy array if not already
    data_array = np.array(data).flatten()
    
    # Create time delay embedding vectors
    vectors = []
    for i in range(len(data_array) - (embed_dim-1) * tau):
        vector = [data_array[i + j*tau] for j in range(embed_dim)]
        vectors.append(vector)
    
    vectors = np.array(vectors)
    
    # Calculate pairwise distances
    dist_matrix = squareform(pdist(vectors, 'euclidean'))
    
    # Set threshold if not provided
    if threshold is None:
        threshold = 0.1 * np.max(dist_matrix)
    
    # Create recurrence matrix (1 for points closer than threshold, 0 otherwise)
    recurrence_matrix = dist_matrix < threshold
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the recurrence matrix
    cax = ax.imshow(recurrence_matrix, cmap=cmap, interpolation='nearest')
    
    # Add colorbar
    plt.colorbar(cax, label='Recurrence')
    
    ax.set_title(f'{title} (d={embed_dim}, τ={tau}, ε={threshold:.3f})')
    ax.set_xlabel('Time Index')
    ax.set_ylabel('Time Index')
    
    # Add metrics text (RQA could be added here in a more comprehensive version)
    recurrence_rate = np.sum(recurrence_matrix) / (recurrence_matrix.shape[0] ** 2)
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    ax.text(0.02, 0.98, f'Recurrence Rate: {recurrence_rate:.4f}', 
            transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    return ax


def plot_phase_space(data, embed_dim=3, tau=1, figsize=(10, 10), 
                    title='Phase Space Plot', alpha=0.6, s=10):
    """
    Create a phase space plot (delay embedding) to reconstruct attractor dynamics.
    
    Parameters
    ----------
    data : array-like
        Time series data
    embed_dim : int, optional
        Embedding dimension (2 or 3)
    tau : int, optional
        Time delay
    figsize : tuple, optional
        Figure size as (width, height) in inches
    title : str, optional
        Title for the plot
    alpha : float, optional
        Transparency of points
    s : int, optional
        Size of points
        
    Returns
    -------
    matplotlib.axes
        The axes containing the plot
    """
    # Convert to numpy array if not already
    data_array = np.array(data).flatten()
    
    if embed_dim not in [2, 3]:
        raise ValueError("embed_dim must be either 2 or 3 for visualization")
    
    if embed_dim == 2:
        # Create 2D embedding
        x = data_array[:-tau]
        y = data_array[tau:]
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot points with connecting lines
        ax.scatter(x, y, alpha=alpha, s=s)
        ax.plot(x, y, alpha=alpha/2, linewidth=0.5)
        
    else:  # embed_dim == 3
        # Create 3D embedding
        x = data_array[:-2*tau]
        y = data_array[tau:-tau]
        z = data_array[2*tau:]
        
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot points with connecting lines
        ax.scatter(x, y, z, alpha=alpha, s=s)
        ax.plot(x, y, z, alpha=alpha/2, linewidth=0.5)
    
    ax.set_title(f'{title} (d={embed_dim}, τ={tau})')
    ax.set_xlabel('$X_t$')
    ax.set_ylabel(f'$X_{{t+{tau}}}$')
    
    if embed_dim == 3:
        ax.set_zlabel(f'$X_{{t+{2*tau}}}$')
    
    return ax

