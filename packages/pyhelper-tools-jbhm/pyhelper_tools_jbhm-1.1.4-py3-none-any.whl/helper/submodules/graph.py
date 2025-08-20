from ..core import pd, BIG_SIZE, NORMAL_SIZE, plt, format_number, sns, mpl, Optional, show_gui_popup, t, np, Union, List, Dict


def hbar(data: pd.Series, title: str, xlabel: str, ylabel: str, save_path: Optional[str] = None, show: bool = True, color: Union[str, List[str]] = "skyblue", **kwargs
):
    try:
        if data.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))

        y_pos = range(len(data))
        bars = plt.barh(y_pos, data.values, color=color)

        plt.yticks(ticks=y_pos, labels=data.index)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(axis="x", alpha=0.3)

        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(            width + 2,
                bar.get_y() + bar.get_height() / 2,
                format_number(width, use_decimals=False),
                va="center",
            )

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def vbar(data: Union[pd.Series, pd.DataFrame],
    title: str,
    xlabel: str,
    ylabel: str,
    save_path: Optional[str] = None,
    show: bool = True,
    color: Union[str, List[str]] = "skyblue",
    **kwargs
):
    try:
        if data.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        bars = plt.bar(data.index, data.values, color=color)

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(axis="y", alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            x = bar.get_x() + bar.get_width() / 2
            plt.text(            x,
                height + (height * 0.02),
                format_number(height, use_decimals=False),
                ha="center",
                va="bottom",
            )

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def pie(valores: Union[List[float], np.ndarray, pd.Series],
    etiquetas: Union[List[str], np.ndarray, pd.Series],
    title: str,
    save_path: Optional[str] = None,
    show: bool = True,
    colors: Optional[List[str]] = None,
    decimales: int = 1,
    **kwargs
):
    try:
        if len(valores) == 0 or len(etiquetas) == 0:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            mpl.use("Agg")

        fig, ax = plt.subplots(figsize=kwargs.get('figsize', NORMAL_SIZE))

        use_labels = len(etiquetas) <= 10
        labels = etiquetas if use_labels else None

        def format_pct(pct):
            return format_number(            pct / 100, use_decimals=True, decimals=decimales, percent=True
            )

        wedges, texts, autotexts = ax.pie(        valores,
            labels=labels,
            autopct=format_pct,
            colors=colors if colors else plt.cm.tab20.colors,
            startangle=90,
            wedgeprops={"edgecolor": "black", "linewidth": 0.8},
            textprops={"fontsize": 8},
        )

        if not use_labels:
            ax.legend(            wedges,
                etiquetas,
                title="Categories",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=8,
                title_fontsize=9,
            )

        ax.set_title(title)
        ax.axis("equal")
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def boxplot(df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: Optional[Union[str, List[str]]] = "tab10",
    **kwargs
):
    try:
        if df.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        if color and not hue:
            sns.boxplot(data=df, x=x, y=y, color=color)
        else:            
            if palette is not None:
                if hue is None:
                    hue = x
                    kwargs["legend"] = False
                kwargs["palette"] = palette
            sns.boxplot(data=df, x=x, y=y, hue=hue, palette=palette)
            
        plt.title(title)
        if x is not None:
            plt.xlabel(x)
        if y is not None:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.4)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def histo(df: pd.DataFrame,
    column: str,
    condition: Optional[pd.Series] = None,
    bins: int = 20,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: str = "skyblue",
    **kwargs
):
    try:
        if column not in df.columns:
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND").format(column))
            return None

        if condition is not None:
            df = df[condition]

        if df[column].dropna().empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', NORMAL_SIZE))
        plt.hist(        df[column].dropna(), bins=bins, color=color, edgecolor="black", alpha=0.7
        )
        plt.title(title or f"Histogram of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def heatmap(data: Union[pd.DataFrame, np.ndarray],
    index_col: Optional[str] = None,
    column_col: Optional[str] = None,
    value_col: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    cmap: str = "YlGnBu",
    annot: bool = True,
    **kwargs
):
    try:
        if isinstance(data, pd.DataFrame):
            if index_col is not None and column_col is not None and value_col is not None:
                # Pivot table case
                if any(col not in data.columns for col in [index_col, column_col, value_col]):
                    show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
                    return None
                    
                tabla = data.groupby([index_col, column_col])[value_col].size().unstack(fill_value=0)
            else:
                # Direct matrix case
                tabla = data
        else:
            # Numpy array case
            tabla = pd.DataFrame(data)

        if tabla.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', NORMAL_SIZE))
        sns.heatmap(        tabla,
            cmap=cmap,
            annot=annot,
            fmt="d" if annot else ".2f",
            annot_kws={"size": 7},
            linewidths=0.1,
            **kwargs
        )
        plt.title(title)
        if index_col:
            plt.ylabel(index_col)
        if column_col:
            plt.xlabel(column_col)
        plt.xticks(rotation=0)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def table(data: Union[List[List], np.ndarray, pd.DataFrame],
    col_labels: Optional[List[str]] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    **kwargs
):
    try:
        if len(data) == 0:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            mpl.use("Agg")

        if isinstance(data, pd.DataFrame):
            if col_labels is None:
                col_labels = data.columns.tolist()
            data = data.values.tolist()
        elif isinstance(data, np.ndarray):
            data = data.tolist()

        fig, ax = plt.subplots(figsize=kwargs.get('figsize', NORMAL_SIZE))
        ax.axis("off")

        tabla = ax.table(cellText=data, colLabels=col_labels, cellLoc="center", loc="top")
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(12)
        tabla.scale(1.5, 1.5)

        if title:
            plt.title(title)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def scatter(df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "viridis",
    **kwargs
):
    try:
        if any(col not in df.columns for col in ([x, y] + ([hue] if hue else []))):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        if hue:
            sns.scatterplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
        else:
            plt.scatter(df[x], df[y], color=color if color else 'blue', **kwargs)
            
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid(True, alpha=0.3)
        if hue:
            plt.legend(title=hue)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def lineplot(df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "tab10",
    **kwargs
):
    try:
        if any(col not in df.columns for col in ([x, y] + ([hue] if hue else []))):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        if hue:
            sns.lineplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
        else:
            plt.plot(df[x], df[y], color=color if color else 'blue', **kwargs)
            
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid(True, alpha=0.3)
        if hue:
            plt.legend(title=hue)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def kdeplot(df: pd.DataFrame,
    column: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "husl",
    **kwargs
):
    try:
        if column not in df.columns or (hue and hue not in df.columns):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', NORMAL_SIZE))
        
        if hue:
            sns.kdeplot(data=df, x=column, hue=hue, palette=palette, **kwargs)
        else:
            sns.kdeplot(data=df[column], color=color if color else 'blue', **kwargs)
            
        plt.title(title or f"KDE Plot of {column}")
        plt.xlabel(column)
        plt.ylabel("Density")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def violinplot(df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "muted",
    **kwargs
):
    try:
        if df.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        if color and not hue:
            sns.violinplot(data=df, x=x, y=y, color=color, **kwargs)
        else:
            if palette is not None:
                if hue is None:
                    hue = x
                    kwargs["legend"] = False
                kwargs["palette"] = palette
            sns.violinplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
            
        plt.title(title)
        if x is not None:
            plt.xlabel(x)
        if y is not None:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def pairplot(df: pd.DataFrame,
    vars: Optional[List[str]] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    palette: str = "husl",
    **kwargs
):
    try:
        if df.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if vars and any(col not in df.columns for col in vars):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        g = sns.pairplot(        df,
            vars=vars if vars else df.select_dtypes(include=[np.number]).columns.tolist(),
            hue=hue,
            palette=palette,
            **kwargs
        )
        
        if title:
            g.figure.suptitle(title, y=1.02)

        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return g.figure
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def countplot(df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "deep",
    **kwargs
):
    try:
        if df.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if (x and x not in df.columns) or (y and y not in df.columns) or (hue and hue not in df.columns):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        if color and not hue:
            sns.countplot(data=df, x=x, y=y, color=color, **kwargs)
        else:            
            if palette is not None:
                if hue is None:
                    hue = x
                    kwargs["legend"] = False
                kwargs["palette"] = palette
            sns.countplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
            
        plt.title(title)
        if x is not None:
            plt.xlabel(x)
        if y is not None:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def lmplot(df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    palette: str = "viridis",
    **kwargs
):
    try:
        if any(col not in df.columns for col in ([x, y] + ([hue] if hue else []))):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        g = sns.lmplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
        
        if title:
            g.figure.suptitle(title, y=1.02)

        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return g.fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def jointplot(df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[str] = None,
    kind: str = "scatter",
    **kwargs
):
    try:
        if any(col not in df.columns for col in [x, y]):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        if hue:
            # For hue, we need to use JointGrid
            g = sns.JointGrid(data=df, x=x, y=y, hue=hue, **kwargs)
            g.plot_joint(sns.scatterplot)
            g.plot_marginals(sns.histplot, kde=True)
        else:
            g = sns.jointplot(data=df, x=x, y=y, color=color, kind=kind, **kwargs)
        
        if title:
            g.figure.suptitle(title, y=1.02)

        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return g.fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def swarmplot(df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "deep",
    **kwargs
):
    try:
        if df.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if (x and x not in df.columns) or (y and y not in df.columns) or (hue and hue not in df.columns):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        if color and not hue:
            sns.swarmplot(data=df, x=x, y=y, color=color, **kwargs)
        else:            
            if palette is not None:
                if hue is None:
                    hue = x
                    kwargs["legend"] = False
                kwargs["palette"] = palette
            sns.swarmplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
            
        plt.title(title)
        if x is not None:
            plt.xlabel(x)
        if y is not None:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def regplot(df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[str] = None,
    **kwargs
):
    try:
        if any(col not in df.columns for col in [x, y]):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        sns.regplot(data=df, x=x, y=y, color=color if color else 'blue', **kwargs)
            
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def barplot(df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "deep",
    **kwargs
):
    try:
        if df.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if (x and x not in df.columns) or (y and y not in df.columns) or (hue and hue not in df.columns):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        if color and not hue:
            sns.barplot(data=df, x=x, y=y, color=color, **kwargs)
        else:
            if palette is not None:
                if hue is None:
                    hue = x
                    kwargs["legend"] = False
                kwargs["palette"] = palette
            sns.barplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
            
        plt.title(title)
        if x is not None:
            plt.xlabel(x)
        if y is not None:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def stripplot(df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "deep",
    **kwargs
):
    try:
        if df.empty:
            show_gui_popup("Error",t("ERROR_EMPTY_DATA"))
            return None

        if (x and x not in df.columns) or (y and y not in df.columns) or (hue and hue not in df.columns):
            show_gui_popup("Error",t("ERROR_COLUMN_NOT_FOUND"))
            return None

        if not show:
            mpl.use("Agg")

        fig = plt.figure(figsize=kwargs.get('figsize', BIG_SIZE))
        
        
        
        if color and not hue:
            sns.stripplot(data=df, x=x, y=y, color=color, **kwargs)
        else:
            if palette is not None:
                if hue is None:
                    hue = x
                    kwargs["legend"] = False
                kwargs["palette"] = palette
            sns.stripplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
            
        plt.title(title)
        if x is not None:
            plt.xlabel(x)
        if y is not None:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")

        if show:
            plt.show()
            return None
        else:
            return fig
            
    except Exception as e:
        show_gui_popup("Error",t("ERROR_PLOT_GENERATION").format(str(e)))
        return None
