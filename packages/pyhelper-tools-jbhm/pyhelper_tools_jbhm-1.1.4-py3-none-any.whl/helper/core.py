import pandas as pd
import numpy as np
import ast
import sys
import os
import time
from pathlib import Path
import json
import csv
import xml.etree.ElementTree as ET
from typing import Union, List, Dict, Set
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import re
import inspect
import asyncio
from collections.abc import Callable
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Optional
import math
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import norm, skew, kurtosis

try:
    from IPython.display import display, Markdown
except ImportError:
    display = None
    Markdown = None


def is_jupyter_notebook():
    try:
        from IPython import get_ipython

        ip = get_ipython()
        if ip is None:
            return False

        shell_name = ip.__class__.__name__
        if shell_name == "ZMQInteractiveShell":
            return True
        else:
            return False
    except ImportError:
        return False


IN_JUPYTER = is_jupyter_notebook()

CONFIG_LANG = "en"
NORMAL_SIZE = (10, 6)
BIG_SIZE = (12, 8)
BG_COLOR = "#2d2d2d"
TEXT_COLOR = "#ffffff"
BTN_BG = "#3d3d3d"
HIGHLIGHT_COLOR = "#4e7cad"


config = {"verbose": True, "default_timeout": 5, "counter": 0}


def show_gui_popup(
    title, content, fig=None, plot_function=None, plot_args=None, preview_mode=False
):
    copy = t("copy")
    close = t("close")
    save = t("save")
    content_text = t("content")
    preview = t("preview")
    gui_error = t("error_in_gui")

    # Set matplotlib backend
    if "ipykernel" in sys.modules:
        mpl.use("module://ipykernel.pylab.backend_inline")
    else:
        mpl.use("Agg")

    current_fig = fig
    if plot_function is not None:
        if plot_args is None:
            plot_args = {}
        current_fig = plot_function(**plot_args)

    if preview_mode:
        if current_fig is not None:
            current_fig.patch.set_facecolor(BG_COLOR)
            for ax in current_fig.get_axes():
                ax.set_facecolor(BG_COLOR)
                ax.title.set_color(TEXT_COLOR)
                ax.xaxis.label.set_color(TEXT_COLOR)
                ax.yaxis.label.set_color(TEXT_COLOR)
                ax.tick_params(colors=TEXT_COLOR)
                for spine in ax.spines.values():
                    spine.set_color(TEXT_COLOR)
        return current_fig

    # Main window setup
    window = tk.Tk()
    window.title(title)
    window.geometry("900x700")
    window.configure(bg=BG_COLOR)

    # Style configuration
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.TFrame", background=BG_COLOR)
    style.configure(
        "Dark.TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Consolas", 10)
    )
    style.configure(
        "Dark.TButton", background=BTN_BG, foreground=TEXT_COLOR, borderwidth=1
    )
    style.map("Dark.TButton", background=[("active", HIGHLIGHT_COLOR)])

    # Main container with proper weight distribution
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    main_frame = ttk.Frame(window, style="Dark.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Notebook for tabs
    notebook = ttk.Notebook(main_frame)
    notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

    # Content tab
    doc_frame = ttk.Frame(notebook, style="Dark.TFrame")
    notebook.add(doc_frame, text=content_text)

    text_area = ScrolledText(
        doc_frame,
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
        selectbackground=HIGHLIGHT_COLOR,
    )
    text_area.pack(expand=True, fill="both", padx=5, pady=5)
    text_area.insert(tk.END, content)
    text_area.config(state="disabled")

    # Visualization handling
    current_fig = fig
    canvas = None

    if fig is not None or plot_function is not None:
        # Preview tab
        graph_frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(graph_frame, text=preview)

        if plot_function is not None:
            if plot_args is None:
                plot_args = {}
            current_fig = plot_function(**plot_args)

        if current_fig is not None:
            # Style the figure
            current_fig.patch.set_facecolor(BG_COLOR)
            for ax in current_fig.get_axes():
                ax.set_facecolor(BG_COLOR)
                ax.title.set_color(TEXT_COLOR)
                ax.xaxis.label.set_color(TEXT_COLOR)
                ax.yaxis.label.set_color(TEXT_COLOR)
                ax.tick_params(colors=TEXT_COLOR)
                for spine in ax.spines.values():
                    spine.set_color(TEXT_COLOR)

            # Display in canvas
            canvas = FigureCanvasTkAgg(current_fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Button functions
    def copy_to_clipboard():
        window.clipboard_clear()
        window.clipboard_append(content)
        window.update()

    def save_image():
        if current_fig is not None:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*"),
                ],
            )
            if filepath:
                current_fig.savefig(filepath, bbox_inches="tight", dpi=300)

    def on_close():
        if current_fig is not None:
            plt.close(current_fig)
        window.quit()
        window.destroy()

    # Button container - using grid for better layout control
    btn_frame = ttk.Frame(main_frame, style="Dark.TFrame")
    btn_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))

    # Configure button frame columns
    btn_frame.grid_columnconfigure(0, weight=1)
    btn_frame.grid_columnconfigure(1, weight=1)

    # Action button (changes function based on tab)
    action_btn = ttk.Button(
        btn_frame, text=copy, command=copy_to_clipboard, style="Dark.TButton"
    )
    action_btn.grid(row=0, column=0, padx=5, sticky="w")

    # Close button
    close_btn = ttk.Button(
        btn_frame, text=close, command=on_close, style="Dark.TButton"
    )
    close_btn.grid(row=0, column=1, padx=5, sticky="e")

    # Tab change handler
    def on_tab_change(event):
        if notebook.index("current") == 1 and current_fig is not None:  # Preview tab
            action_btn.config(text=save, command=save_image)
        else:
            action_btn.config(text=copy, command=copy_to_clipboard)

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    # Initial button state
    if fig is not None or plot_function is not None:
        if notebook.index("current") == 1:  # If preview tab is active
            action_btn.config(text=save, command=save_image)

    # Jupyter Notebook specific handling
    if "ipykernel" in sys.modules:
        from IPython.display import display
        import ipywidgets as widgets

        output = widgets.Output()
        display(output)

        def run_in_jupyter():
            with output:
                try:
                    window.mainloop()
                except Exception as e:
                    print(f"{gui_error}: {str(e)}")

        window.after(100, run_in_jupyter)
    else:

        window.mainloop()

    if current_fig is not None:
        plt.close(current_fig)


TRANSLATIONS_PATH = Path(__file__).parent / "translations.json"
TRANSLATIONS = {}
_translations = {}


def t(key: str, lang: str = None) -> str:
    if not key:
        return t("missing_translation_key").format(key=key)

    lang = lang or CONFIG_LANG

    entry = _translations.get(key, {})

    if lang not in entry:
        return f"[{key}]"

    return entry[lang]


def load_user_translations(lang_path: str = "lang.json"):
    global _translations

    user_translations = {}
    path = Path(lang_path)

    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_translations = json.load(f)
        except Exception as e:
            show_gui_popup(
                t("warning"), t("load_user_translations_error").format(error=str(e))
            )

    _translations = TRANSLATIONS.copy()
    _translations.update(user_translations)


if TRANSLATIONS_PATH.exists():
    with open(TRANSLATIONS_PATH, encoding="utf-8") as f:
        TRANSLATIONS = json.load(f)
        _translations = TRANSLATIONS.copy()

else:
    show_gui_popup(t("warning"), t("translations_not_found_warning"))


REGISTRY = {}


def register(name=None):
    """
    Decorator to register a function or class in the global REGISTRY.
    Allows other parts of the package to dynamically access utilities by name.
    """

    def wrapper(fn):
        key = name or fn.__name__
        REGISTRY[key] = fn
        return fn

    return wrapper


def fig_to_img(fig):
    """Convierte una figura matplotlib a una imagen para mostrar en otro gráfico"""
    fig.canvas.draw()
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return img


def generate_all_previews(preview_data):
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    import numpy as np

    preview_title = t("function_preview_title")
    preview_error = t("preview_error_message")

    # Filtrar solo las funciones que devuelven gráficos
    graph_previews = {}
    for func_name, data in preview_data.items():
        try:
            result = data["preview_func"]()
            if hasattr(result, "figure"):
                graph_previews[func_name] = data
        except:
            pass

    num_funcs = len(graph_previews)
    if num_funcs == 0:
        return None

    # Cada gráfico ocupa 6 de alto y 8 de ancho
    rows = (num_funcs + 1) // 2
    fig_height = rows * 6
    fig_width = 18  # ancho generoso
    fig = plt.figure(figsize=(fig_width, fig_height), tight_layout=True)
    gs = GridSpec(rows, 2, figure=fig)

    for idx, (func_name, data) in enumerate(graph_previews.items()):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])

        try:
            result = data["preview_func"]()

            if hasattr(result, "figure"):
                result.canvas.draw()
                img = np.frombuffer(result.canvas.tostring_rgb(), dtype=np.uint8)
                img = img.reshape(result.canvas.get_width_height()[::-1] + (3,))
                ax.imshow(img)
                ax.axis("off")
                plt.close(result.figure)

        except Exception as e:
            ax.text(
                0.5,
                0.5,
                preview_error.format(error=str(e)),
                ha="center",
                va="center",
                color="red",
            )
            ax.axis("off")

        ax.set_title(f"{func_name}", fontsize=12)

    return fig


def help(type: str = None):

    from .submodules import (
        hbar,
        vbar,
        pie,
        normalize,
        get_moda,
        get_media,
        get_median,
        boxplot,
        get_rank,
        get_var,
        get_desv,
        histo,
        disp,
        table,
        conditional,
        heatmap,
        call,
        Switch,
        scatter,
        lineplot,
        kdeplot,
        violinplot,
        pairplot,
        countplot,
        lmplot,
        jointplot,
        swarmplot,
        regplot,
        barplot,
        stripplot,
    )

    # Translation strings
    preview_error_text = t("preview_error")
    gui_error_text = t("error_in_gui")
    error_text = t("help_error")
    function_preview_title = t("function_preview_title")
    preview_error_msg = t("preview_error_message")
    async_preview_note = t("async_preview_not_available")
    preview_text = t("preview")
    example_text = t("example")
    description = t("description")
    available_funcs_text = t("help_available_functions")
    usage_text = t("help_usage")
    all_title_text = t("title_all")

    help_map = {
        "get_moda": {
            description: t("get_moda"),
            example_text: "get_moda(np.array([1, 2, 2, 3, 3, 3]), with_repetition=True, decimals=2)",
            preview_text: lambda: show_gui_popup(
                title="Moda",
                content=get_moda(
                    np.array([1, 2, 2, 3, 3, 3]), with_repetition=True, decimals=2
                ),
                preview_mode=True,
            ),
        },
        "get_media": {
            description: t("get_media"),
            example_text: "get_media(np.array([10, 20, 30, 40]), nan=False, decimals=2)",
            preview_text: lambda: show_gui_popup(
                title="Media",
                content=get_media(np.array([10, 20, 30, 40]), nan=False, decimals=2),
                preview_mode=True,
            ),
        },
        "get_median": {
            description: t("get_median"),
            example_text: "get_median(np.array([10, 20, 30, 40]), nan=False, decimals=2)",
            preview_text: lambda: show_gui_popup(
                title="Mediana",
                content=get_median(np.array([10, 20, 30, 40]), nan=False, decimals=2),
                preview_mode=True,
            ),
        },
        "get_rank": {
            description: t("get_rank"),
            example_text: 'get_rank(pd.DataFrame({"A": [10, 20, 30]}), "A", decimals=2)',
            preview_text: lambda: show_gui_popup(
                title="Rank",
                content=get_rank(pd.DataFrame({"A": [10, 20, 30]}), "A", decimals=2),
                preview_mode=True,
            ),
        },
        "get_var": {
            description: t("get_var"),
            example_text: 'get_var(pd.DataFrame({"A": [10, 20, 30]}), "A", decimals=2)',
            preview_text: lambda: show_gui_popup(
                title="Varianza",
                content=get_var(pd.DataFrame({"A": [10, 20, 30]}), "A", decimals=2),
                preview_mode=True,
            ),
        },
        "get_desv": {
            description: t("get_desv"),
            example_text: 'get_desv(pd.DataFrame({"A": [10, 20, 30]}), "A", decimals=2)',
            preview_text: lambda: show_gui_popup(
                title="Desviación Estándar",
                content=get_desv(pd.DataFrame({"A": [10, 20, 30]}), "A", decimals=2),
                preview_mode=True,
            ),
        },
        "disp": {
            description: t("disp"),
            example_text: 'disp(pd.DataFrame({"A": [10, 20, 30]}), "A")',
            preview_text: lambda: show_gui_popup(
                title="Disp",
                content=disp(pd.DataFrame({"A": [10, 20, 30]}), "A"),
                preview_mode=True,
            ),
        },
        "normalize": {
            description: t("normalize"),
            example_text: "normalize(np.array([1, 2, 3, 4, 5]))",
            preview_text: lambda: show_gui_popup(
                title="Normalize",
                content=normalize(np.array([1, 2, 3, 4, 5])),
                preview_mode=True,
            ),
        },
        "conditional": {
            description: t("conditional"),
            example_text: """
conditional(
    pd.DataFrame({"A": [1, 2, 3, 4]}),
    conditions=[lambda df: df["A"] < 3, lambda df: df["A"] >= 3],
    results=["Low", "High"],
    column_name="Category"
)
    """,
            preview_text: lambda: (
                lambda df: show_gui_popup(
                    title="Conditional Example",
                    content=pd.concat(
                        [
                            pd.DataFrame({"Antes": df["A"]}),
                            conditional(
                                df.copy(),
                                conditions=[
                                    lambda df: df["A"] < 3,
                                    lambda df: df["A"] >= 3,
                                ],
                                results=["Low", "High"],
                                column_name="Category",
                            ),
                        ],
                        axis=1,
                    ),
                    preview_mode=True,
                )
            )(pd.DataFrame({"A": [1, 2, 3, 4]})),
        },
        "hbar": {
            description: t("hbar"),
            example_text: 'hbar(pd.Series([30, 70], index=["A", "B"]), title="My Chart", xlabel="Categories", ylabel="Values")',
            preview_text: lambda: hbar(
                pd.Series([30, 70], index=["A", "B"]),
                title="My Chart",
                xlabel="Categories",
                ylabel="Values",
                show=IN_JUPYTER,
            ),
        },
        "vbar": {
            description: t("vbar"),
            example_text: 'vbar(pd.Series([30, 70], index=["A", "B"]), title="Vertical Chart", xlabel="Categories", ylabel="Values")',
            preview_text: lambda: vbar(
                pd.Series([30, 70], index=["A", "B"]),
                title="Vertical Chart",
                xlabel="Categories",
                ylabel="Values",
                show=IN_JUPYTER,
            ),
        },
        "pie": {
            description: t("pie"),
            example_text: 'pie([50, 50], ["Cats", "Dogs"], title="Pets")',
            preview_text: lambda: pie(
                [50, 50],
                ["Cats", "Dogs"],
                title="Pets",
                show=IN_JUPYTER,
            ),
        },
        "boxplot": {
            description: t("boxplot"),
            example_text: 'boxplot(pd.DataFrame({"Values": [10, 20, 30]}), y="Values", title="Box Plot")',
            preview_text: lambda: boxplot(
                pd.DataFrame({"Values": [10, 20, 30]}),
                y="Values",
                title="Box Plot",
                show=IN_JUPYTER,
            ),
        },
        "histo": {
            description: t("histo"),
            example_text: 'histo(pd.DataFrame({"Values": [1,2,2,3,3,3,4]}), column="Values", bins=5, title="Histogram")',
            preview_text: lambda: histo(
                pd.DataFrame({"Values": [1, 2, 2, 3, 3, 3, 4]}),
                column="Values",
                bins=5,
                title="Histogram",
                show=IN_JUPYTER,
            ),
        },
        "heatmap": {
            description: t("heatmap"),
            example_text: """
heatmap(
    pd.DataFrame({"X": ["A", "A", "B"], "Y": ["C", "D", "C"], "Value": [1, 2, 3]}),
    index_col="X", column_col="Y", value_col="Value", title="Heatmap"
)
        """,
            preview_text: lambda: heatmap(
                pd.DataFrame(
                    {"X": ["A", "A", "B"], "Y": ["C", "D", "C"], "Value": [1, 2, 3]}
                ),
                index_col="X",
                column_col="Y",
                value_col="Value",
                title="Heatmap",
                show=IN_JUPYTER,
            ),
        },
        "table": {
            description: t("table"),
            example_text: 'table(pd.DataFrame({"A": [1, 2], "B": [3, 4]}), col_labels=["A", "B"], title="Table")',
            preview_text: lambda: table(
                pd.DataFrame({"A": [1, 2], "B": [3, 4]}),
                col_labels=["A", "B"],
                title="Table",
                show=IN_JUPYTER,
            ),
        },
        "scatter": {
            description: t("scatter"),
            example_text: 'scatter(df, x="age", y="income", hue="gender", title="Age vs Income")',
            preview_text: lambda: scatter(
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40],
                        "income": [40000, 45000, 60000, 80000],
                        "gender": ["M", "F", "M", "F"],
                    }
                ),
                x="age",
                y="income",
                hue="gender",
                title="Age vs Income",
                show=IN_JUPYTER,
            ),
        },
        "lineplot": {
            description: t("lineplot"),
            example_text: 'lineplot(df, x="year", y="sales", hue="product", title="Sales Trend")',
            preview_text: lambda: lineplot(
                pd.DataFrame(
                    {
                        "year": [2018, 2019, 2020, 2021],
                        "sales": [100, 120, 150, 180],
                        "product": ["A", "A", "B", "B"],
                    }
                ),
                x="year",
                y="sales",
                hue="product",
                title="Sales Trend",
                show=IN_JUPYTER,
            ),
        },
        "kdeplot": {
            description: t("kdeplot"),
            example_text: 'kdeplot(df, column="age", title="Age Distribution")',
            preview_text: lambda: kdeplot(
                pd.DataFrame({"age": [25, 30, 35, 40]}),
                column="age",
                title="Age Distribution",
                show=IN_JUPYTER,
            ),
        },
        "violinplot": {
            description: t("violinplot"),
            example_text: 'violinplot(df, x="category", y="value", title="Value Distribution")',
            preview_text: lambda: violinplot(
                pd.DataFrame(
                    {
                        "category": ["A", "A", "B", "B"],
                        "value": [10, 12, 15, 18],
                    }
                ),
                x="category",
                y="value",
                title="Value Distribution",
                show=IN_JUPYTER,
            ),
        },
        "pairplot": {
            description: t("pairplot"),
            example_text: 'pairplot(df, vars=["age", "income"], title="Pairplot Example")',
            preview_text: lambda: pairplot(
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40],
                        "income": [40000, 45000, 60000, 80000],
                    }
                ),
                vars=["age", "income"],
                title="Pairplot Example",
                show=IN_JUPYTER,
            ),
        },
        "countplot": {
            description: t("countplot"),
            example_text: 'countplot(df, x="category", title="Category Count")',
            preview_text: lambda: countplot(
                pd.DataFrame({"category": ["A", "B", "A", "C"]}),
                x="category",
                title="Category Count",
                show=IN_JUPYTER,
            ),
        },
        "lmplot": {
            description: t("lmplot"),
            example_text: 'lmplot(df, x="age", y="income", hue="gender", title="Linear Model")',
            preview_text: lambda: lmplot(
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40],
                        "income": [40000, 45000, 60000, 80000],
                        "gender": ["M", "F", "M", "F"],
                    }
                ),
                x="age",
                y="income",
                hue="gender",
                title="Linear Model",
                show=IN_JUPYTER,
            ),
        },
        "jointplot": {
            description: t("jointplot"),
            example_text: 'jointplot(df, x="age", y="income", kind="scatter", title="Joint Plot")',
            preview_text: lambda: jointplot(
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40],
                        "income": [40000, 45000, 60000, 80000],
                    }
                ),
                x="age",
                y="income",
                kind="scatter",
                title="Joint Plot",
                show=IN_JUPYTER,
            ),
        },
        "swarmplot": {
            description: t("swarmplot"),
            example_text: 'swarmplot(df, x="category", y="value", title="Swarm Plot")',
            preview_text: lambda: swarmplot(
                pd.DataFrame(
                    {
                        "category": ["A", "A", "B", "B"],
                        "value": [10, 12, 15, 18],
                    }
                ),
                x="category",
                y="value",
                title="Swarm Plot",
                show=IN_JUPYTER,
            ),
        },
        "regplot": {
            description: t("regplot"),
            example_text: 'regplot(df, x="age", y="income", title="Regression Plot")',
            preview_text: lambda: regplot(
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40],
                        "income": [40000, 45000, 60000, 80000],
                    }
                ),
                x="age",
                y="income",
                title="Regression Plot",
                show=IN_JUPYTER,
            ),
        },
        "barplot": {
            description: t("barplot"),
            example_text: 'barplot(df, x="category", y="value", title="Bar Plot")',
            preview_text: lambda: barplot(
                pd.DataFrame({"category": ["A", "B", "C"], "value": [10, 15, 8]}),
                x="category",
                y="value",
                title="Bar Plot",
                show=IN_JUPYTER,
            ),
        },
        "stripplot": {
            description: t("stripplot"),
            example_text: 'stripplot(df, x="category", y="value", title="Strip Plot")',
            preview_text: lambda: stripplot(
                pd.DataFrame(
                    {
                        "category": ["A", "A", "B", "B"],
                        "value": [10, 12, 15, 18],
                    }
                ),
                x="category",
                y="value",
                title="Strip Plot",
                show=IN_JUPYTER,
            ),
        },
    }

    functions = sorted(help_map.keys())

    if type is None:
        if IN_JUPYTER:
            display(Markdown(f"**{available_funcs_text}**"))
            for func in functions:
                display(Markdown(f"- `{func}`"))
            display(Markdown(f"\n*{usage_text}*"))
        else:
            func_list = "\n".join(f"- {func}" for func in functions)
            show_gui_popup(
                "Help", f"{available_funcs_text}\n{func_list}\n\n{usage_text}"
            )
        return

    if not isinstance(type, str):
        msg = t("error_type")
        if IN_JUPYTER:
            display(Markdown(f"**Error:** {msg}"))
        else:
            show_gui_popup(title=gui_error_text, content=msg)
        return

    type = type.lower()

    if type == "all":
        full_doc = []
        preview_data = {}

        for func_name in functions:
            entry = help_map.get(func_name, {})
            doc = entry.get(description, "")
            example = entry.get(example_text, "")

            func_doc = f"{func_name.upper()}\n\n{doc}\n\nExample:\n{example}"
            full_doc.append(func_doc)

            if preview_text in entry:
                preview_data[func_name] = {
                    example_text: example,
                    "preview_func": entry[preview_text],
                }

        full_doc_text = (
            "\n\n"
            + ("=" * 50).join("\n\n")
            + "\n\n".join(full_doc)
            + "\n\n"
            + ("=" * 50)
        )

        if IN_JUPYTER:
            from IPython.display import display, Markdown
            import matplotlib.pyplot as plt

            display(Markdown(full_doc_text))
            for func_name, data in preview_data.items():
                display(Markdown(f"**Preview for {func_name}**"))
                try:
                    result = data["preview_func"]()
                    if hasattr(result, "figure"):
                        display(result.figure)
                        plt.close(result.figure)
                    else:
                        display(Markdown(f"```\n{str(result)}\n```"))
                except Exception as e:
                    display(Markdown(f"**Error in preview:**\n```\n{str(e)}\n```"))
        else:

            show_gui_popup(
                all_title_text,
                full_doc_text,
                plot_function=lambda: generate_all_previews(preview_data),
            )
        return

    if type in functions:
        doc = t(type)
        entry = help_map.get(type, {})
        example = entry.get(example_text, "")
        preview_func = entry.get(preview_text)

        if IN_JUPYTER:
            from IPython.display import display, Markdown

            output = f"**{type.upper()}**\n```python\n{doc.strip()}\n```"
            if example:
                output += f"\n\n**{example_text}:**\n```python\n{example}\n```"
            display(Markdown(output))

            if preview_func:
                try:
                    print(f"\n**{preview_text}:**")
                    preview_func()
                except Exception as e:
                    display(Markdown(f"**{preview_error_text}:**\n```\n{str(e)}\n```"))
        else:
            full_text = doc.strip()
            if example:
                full_text += f"\n\n{example_text}:\n{example}"

            fig = None
            if preview_func:
                try:
                    result = preview_func()
                    if hasattr(result, "figure"):
                        fig = result.figure
                except Exception as e:
                    from tkinter import messagebox

                    messagebox.showerror(f"{preview_error_text} {type}", str(e))

            show_gui_popup(type.upper(), full_text, fig=fig)
    else:
        error_msg = error_text.format(type)
        if IN_JUPYTER:
            from IPython.display import display, Markdown

            display(Markdown(f"**{error_msg}**"))
        else:
            show_gui_popup(gui_error_text, error_msg)


def format_number(
    value: float, use_decimals: bool = True, decimals: int = 2, percent: bool = False
) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"

    if percent:
        value *= 100

    if use_decimals:
        formatted = f"{value:,.{decimals}f}"
    else:
        formatted = f"{int(round(value)):,}"

    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")

    if percent:
        formatted += "%"

    return formatted


def set_language(lang: str):
    global CONFIG_LANG
    if lang not in next(iter(TRANSLATIONS.values())).keys():
        raise ValueError(f"Language '{lang}' is not available.")
    CONFIG_LANG = lang


__all__ = [
    "sys",
    "ast",
    "pd",
    "Path",
    "Dict",
    "Set",
    "json",
    "csv",
    "ET",
    "mpl",
    "Union",
    "List",
    "sns",
    "tk",
    "messagebox",
    "ScrolledText",
    "np",
    "plt",
    "re",
    "inspect",
    "asyncio",
    "Callable",
    "time",
    "os",
    "re",
    "help",
    "format_number",
    "config",
    "REGISTRY",
    "register",
    "NORMAL_SIZE",
    "BIG_SIZE",
    "CONFIG_LANG",
    "set_language",
    "t",
    "show_gui_popup",
    "load_user_translations",
    "Optional",
    "filedialog",
    "math",
    "StandardScaler",
    "PCA",
    "norm",
    "skew",
    "kurtosis",
]
