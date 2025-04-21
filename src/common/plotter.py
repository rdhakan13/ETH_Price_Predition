import os
import logging
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Any

logger = logging.getLogger(__name__)


class Plotter:
    def __init__(self, root_dir:str):
        """
        Initialize the Plotter with the parent directory.

        Parameters:
            root_dir (str): The root directory where results will be saved.

        Attributes:
            root_dir (str): The root directory where results will be saved.
            title (str): The title of the plot.
            filepath (str): The filepath to save the plot.
            fig (plt.Figure): The figure object for the plot.
            ax (plt.Axes): The axes object for the plot.
        """
        self.root_dir = root_dir
        self.title = None
        self.filepath = None
        self.fig = None
        self.ax = None

    def configure_style(self, style: str = "whitegrid", palette: str = "deep") -> None:
        """
        Configure the style and palette of the plots.

        Parameters:
            style (str, optional): The style of the plot. Default is "whitegrid".
            palette (str, optional): The color palette of the plot. Default is "deep".

        Returns:
            None
        """
        sns.set(style=style, palette=palette)

    def plot_barchart(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        figsize: tuple[float,float] = (10, 6),
        **kwargs,
    ) -> None:
        """
        Generate a bar chart for the given DataFrame.

        Parameters:
            df (pd.DataFrame, optional): DataFrame containing the data to plot.
            x (str, optional): Column name for the x-axis. Default is None.
            y (str, optional): Column name for the y-axis. Default is None.
            figsize (tuple, optional): The size of the figure. Default is (10, 6).
            kwargs (dict, optional): Additional keyword arguments for the plot.

        Returns:
            None
        """
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.filepath = f"{self.root_dir}\\reports\\figures\\bar_charts"
        kwargs = self._handle_none_graph_kwargs(kwargs)
        if kwargs.get("stacked") is True:
            df.plot(kind="bar", ax=self.ax, **kwargs)
            plt.xlabel(x.title())
            plt.ylabel(y.title())
            if kwargs.get("legend") is not None:
                plt.legend(title=kwargs.get("legend"))
            if kwargs.get("bar_label") is True:
                for c in self.ax.containers:
                    labels = [
                        int(v.get_height()) if v.get_height() > 0 else "" for v in c
                    ]
                    self.ax.bar_label(
                        c,
                        labels=labels,
                        label_type="center",
                        fontweight="bold",
                        color="black",
                    )
        else:
            df.plot(kind="bar", x=x, y=y, ax=self.ax, **kwargs)
            plt.xlabel(x.title())
            plt.ylabel(y.title())
        if self.title is not None:
            plt.title(self.title.title())
        plt.show()

    def plot_correlation_matrix(
        self,
        df: pd.DataFrame,
        method: str = "spearmen",
        figsize: tuple[float,float] = (10, 8),
        **kwargs,
    ) -> None:
        """
        Generate a correlation matrix heatmap for the given DataFrame.

        Parameters:
            df (pd.DataFrame, optional): DataFrame containing the data to plot.
            method (str, optional): The method to compute correlation ('pearson', 'kendall', 'spearman'). Default is "spearmen".
            figsize (tuple, optional): The size of the figure. Default is (10, 8).
            **kwargs (dict, optional): Additional keyword arguments for the plot.

        Returns:
            None
        """
        corr_df = df.apply(pd.to_numeric, errors="coerce").corr(method=method)
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.filepath = f"{self.root_dir}\\reports\\figures\\correlation_matrix"
        self.title = f"{method.title()} Correlation Matrix Heatmap"
        kwargs = self._handle_none_graph_kwargs(kwargs)
        if kwargs.get("mask") is True:
            mask_df = np.abs(corr_df) < kwargs.get("threshold")
            kwargs.pop("mask")
            kwargs.pop("threshold")
            kwargs = kwargs | {"mask": mask_df}
        sns.heatmap(
            corr_df, annot=True, cmap="coolwarm", center=0, **kwargs, ax=self.ax
        )
        if self.title is not None:
            plt.title(self.title.title())
        plt.show()

    def plot_violin_plot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        figsize: tuple[float,float] = (10, 8),
        stripplot: bool = False,
        jitter: float = 0.1,
        **kwargs,
    ) -> None:
        """
        Generate a violin plot with optional scatter overlay.

        Parameters:
            df (pd.DataFrame): DataFrame containing the data to plot.
            x (str, optional): Column name for the x-axis. Default is None.
            y (str, optional): Column name for the y-axis. Default is None.
            figsize (tuple, optional): The size of the figure. Default is (10, 8).
            stripplot (bool, optional): Whether to overlay a stripplot. Default is False.
            jitter (float, optional): Amount of jitter to apply to the stripplot. Default is 0.1.
            **kwargs (dict, optional): Additional keyword arguments for the plot.

        Returns:
            None
        """
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.filepath = f"{self.root_dir}\\reports\\figures\\violin_plots"
        kwargs = self._handle_none_graph_kwargs(kwargs)
        sns.violinplot(data=df, inner="quartile", x=x, y=y, ax=self.ax, **kwargs)
        if stripplot is True:
            sns.stripplot(
                data=df,
                x=x,
                y=y,
                jitter=jitter,
                dodge=True,
                marker="o",
                alpha=0.5,
                color="red",
                ax=self.ax,
            )
        if self.title is not None:
            plt.title(self.title.title())
        plt.xlabel(x.title())
        plt.ylabel(y.title())
        plt.show()

    def plot_boxplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        figsize: tuple[float,float] = (10, 8),
        **kwargs,
    ) -> None:
        """
        Generate boxplots for the given DataFrame.

        Parameters:
            df (pd.DataFrame): DataFrame containing the data to plot.
            x (str, optional): Column name for the x-axis. Default is None.
            y (str, optional): Column name for the y-axis. Default is None.
            figsize (tuple, optional): The size of the figure. Default is (10, 8).
            **kwargs (dict, optional): Additional keyword arguments for the plot.

        Returns:
            None
        """
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.filepath = f"{self.root_dir}\\reports\\figures\\boxplots"
        kwargs = self._handle_none_graph_kwargs(kwargs)
        sns.boxplot(data=df, x=x, y=y, ax=self.ax, **kwargs)
        if self.title is not None:
            plt.title(self.title.title())
        plt.xlabel(x.title())
        plt.ylabel(y.title())
        if kwargs.get("hue") is not None:
            plt.legend(title=kwargs.get("hue"))
        plt.show()

    def plot_scatterplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        figsize: tuple[float,float] = (10, 8),
        **kwargs,
    ) -> None:
        """
        Generate a scatter plot for the given DataFrame.

        Parameters:
            df (pd.DataFrame): DataFrame containing the data to plot.
            x (str, optional): Column name for the x-axis. Default is None.
            y (str, optional): Column name for the y-axis. Default is None.
            figsize (tuple, optional): The size of the figure. Default is (10, 8).
            **kwargs (dict, optional): Additional keyword arguments for the plot.

        Returns:
            None
        """
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.filepath = f"{self.root_dir}\\reports\\figures\\scatter_plots"
        kwargs = self._handle_none_graph_kwargs(kwargs)
        sns.scatterplot(data=df, x=x, y=y, ax=self.ax, **kwargs)
        if self.title is not None:
            plt.title(self.title.title())
        plt.xlabel(x.title())
        plt.ylabel(y.title())
        plt.show()

    def plot_lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        figsize: tuple[float,float] = (10, 8),
        **kwargs,
    ) -> None:
        """
        Generate a line plot for the given DataFrame.

        Parameters:
            df (pd.DataFrame): DataFrame containing the data to plot.
            x (str, optional): Column name for the x-axis. Default is None.
            y (str, optional): Column name for the y-axis. Default is None.
            figsize (tuple, optional): The size of the figure. Default is (10, 8).
            **kwargs (dict, optional): Additional keyword arguments for the plot.

        Returns:
            None
        """
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.filepath = f"{self.root_dir}\\reports\\figures\\line_plots"
        kwargs = self._handle_none_graph_kwargs(kwargs)
        sns.lineplot(data=df, x=x, y=y, ax=self.ax, **kwargs)
        if self.title is not None:
            plt.title(self.title.title())
        plt.xlabel(x.title())
        plt.ylabel(y.title())
        plt.show()

    def save_graph(
        self, filepath: str, format: str = "jpg", dpi: int = 400, 
    ) -> None:
        """
        Save the current graph to a file.

        Parameters:
            format (str, optional): The format to save the file in. Default is "pdf".
            dpi (int, optional): The resolution of the saved file. Default is 300.
            filepath (str, optional): Filepath to save the graph.

        Returns:
            None
        """
        if filepath is not None:
            self.filepath = filepath
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        self.fig.savefig(
            f"{self.filepath}\\{self.title}.{format}", format=format, dpi=dpi
        )

    def _handle_none_graph_kwargs(self, kwargs: dict[str,Any]) -> dict:
        """
        Handle the None values in the graph kwargs.

        Parameters:
            kwargs (dict): The keyword arguments for the plot.

        Returns:
            dict: The updated keyword arguments.
        """
        if kwargs.get("title") is not None:
            self.title = kwargs.get("title").title()
            kwargs.pop("title")
        else:
            self.title = None

        if kwargs.get("filepath") is not None:
            self.filepath = kwargs.get("filepath")
            kwargs.pop("filepath")

        return kwargs
