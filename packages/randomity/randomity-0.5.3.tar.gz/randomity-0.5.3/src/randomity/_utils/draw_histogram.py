import matplotlib.pyplot as plt

from .check_param import _checkParam_histogram

def _draw_histogram(data, 
                   bins:int=10, 
                   title:str='', 
                   xlabel:str='Value', 
                   ylabel:str='Frequency', 
                   color:str='gray', 
                   alpha:float=1.0, 
                   edgecolor:str='',
                   grid:bool=True) -> None:
    """
    Draws a histogram from the given data.

    Args:
        data (list): List of values to plot. Required.
        bins (int or list): Number of bins or specific bin edges. Default is 10.     
        title (str): Title of the histogram. Default is no title.
        xlabel (str): Label for the x-axis. Default is 'Value'.
        ylabel (str): Label for the y-axis. Default is 'Frequency'.
        color (str): Color of the bars. Default is 'blue'.
        alpha (float): Transparency level of the bars. Default is 1.0.
        edgecolor (str): Color of the edges of the bars. Default is no edge color.
        grid (bool): Whether to show grid lines. Default is True.

    Returns:
        None - Displays the histogram.
    """

    _checkParam_histogram(data, bins, title, xlabel, ylabel, color, alpha, edgecolor, grid)

    try:
        plt.hist(data, bins=bins, color=color, alpha=alpha, edgecolor=edgecolor)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if grid:
            plt.grid(axis='y', alpha=0.75)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error drawing histogram: {e}")